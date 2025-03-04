from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import logging
import requests
import io
import numpy as np
from django.db import connection
import traceback
import json
from datetime import datetime
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


@api_view(["POST"])
def extract_order_data(request):
    """
    API endpoint that returns sales volume based on optional filters.
    """
    try:
        csv_drive_urls = request.data.get("urls", [])
        csv_dataframes = []

        for drive_url in csv_drive_urls:
            try:
                google_file_id = drive_url.split("/d/")[1].split("/")[0]
                download_url = f"https://drive.google.com/uc?id={google_file_id}"
                response = requests.get(download_url, verify=False)
                response.raise_for_status()
                csv_data = pd.read_csv(io.StringIO(response.text))
                csv_dataframes.append(csv_data)
            except Exception as e:
                return Response(
                    {"status": "error", "message": f"Error reading CSV file: {str(e)}"},
                    status=400,
                )

        merged_dataframe = pd.concat(csv_dataframes, ignore_index=True)
        merged_dataframe = merged_dataframe.replace({np.nan: None})
        records = merged_dataframe.to_dict(orient="records")

        try:
            with connection.cursor() as cursor:
                # Insert platforms
                platforms = {
                    record["Platform"] for record in records if record["Platform"]
                }
                platform_values = [(name,) for name in platforms]
                execute_values(
                    cursor,
                    "INSERT INTO platform (name) VALUES %s ON CONFLICT (name) DO NOTHING",
                    platform_values,
                )

                # Get platform mapping
                cursor.execute(
                    "SELECT name, id FROM platform WHERE name = ANY(%s)",
                    [list(platforms)],
                )
                platform_map = dict(cursor.fetchall())

                # Insert products
                products = {
                    (
                        record["ProductID"],
                        record["ProductName"],
                        record["Category"],
                        platform_map[record["Platform"]],
                    )
                    for record in records
                    if record["ProductID"]
                }
                product_values = [
                    (pid, name, category, platform_id)
                    for pid, name, category, platform_id in products
                ]
                execute_values(
                    cursor,
                    """
                    INSERT INTO product (id, name, category, platform_id)
                    VALUES %s
                    ON CONFLICT (id, name, category, platform_id) DO NOTHING
                    """,
                    product_values,
                )

                # Insert customers
                customers = {
                    (
                        record["CustomerID"],
                        record["CustomerName"],
                        record["ContactEmail"],
                        platform_map[record["Platform"]],
                    )
                    for record in records
                    if record["CustomerID"]
                }
                customer_values = [
                    (cid, name, email, platform_id)
                    for cid, name, email, platform_id in customers
                ]
                execute_values(
                    cursor,
                    """
                    INSERT INTO customer (id, name, contact_email, platform_id)
                    VALUES %s ON CONFLICT (id) DO NOTHING
                    """,
                    customer_values,
                )

                # Insert addresses
                addresses = []
                for record in records:
                    if record["DeliveryAddress"] and record["CustomerID"]:
                        street, city_state = record["DeliveryAddress"].split(", ", 1)
                        city, state = city_state.split(", ")
                        city = city.replace("City-", "")
                        state = state.replace("State-", "")
                        address_id = f"ADDR-{record['CustomerID']}-{city}-{state}"
                        addresses.append(
                            (address_id, street, city, state, 0, record["CustomerID"])
                        )

                execute_values(
                    cursor,
                    """
                    INSERT INTO customer_address_details 
                    (id, street, city, state, pincode, customer_id)
                    VALUES %s ON CONFLICT (id) DO NOTHING
                    """,
                    list(set(addresses)),
                )

                # Insert orders
                order_values = []
                for record in records:
                    if record["OrderID"]:
                        address_id = f"ADDR-{record['CustomerID']}-{record['DeliveryAddress'].split(', ')[1].replace('City-', '')}-{record['DeliveryAddress'].split(', ')[2].replace('State-', '')}"
                        meta_data = {
                            "coupon_used": record["CouponUsed"],
                            "return_window": record["ReturnWindow"],
                            "prime_delivery": record["PrimeDelivery"],
                            "warehouse_location": record["WarehouseLocation"],
                            "reseller_name": record["ResellerName"],
                            "commission_percentage": record["CommissionPercentage"],
                            "phone_number": record["PhoneNumber"],
                        }
                        order_values.append(
                            (
                                record["OrderID"],
                                datetime.strptime(
                                    record["DateOfSale"], "%Y-%m-%d"
                                ).date(),
                                record["CustomerID"],
                                address_id,
                                platform_map[record["Platform"]],
                                datetime.strptime(
                                    record["DeliveryDate"], "%Y-%m-%d"
                                ).date(),
                                record["DeliveryStatus"],
                                json.dumps(meta_data),
                            )
                        )

                execute_values(
                    cursor,
                    """
                    INSERT INTO orders
                    (id, date_of_sale, customer_id, customer_address_details_id, 
                     platform_id, delivery_date, delivery_status, meta_data)
                    VALUES %s ON CONFLICT (id) DO NOTHING
                    """,
                    order_values,
                )

                # Insert order details
                order_details_values = [
                    (record["OrderID"], record["ProductID"], record["SellingPrice"])
                    for record in records
                    if record["OrderID"] and record["ProductID"]
                ]

                execute_values(
                    cursor,
                    """
                    INSERT INTO order_details (order_id, product_id, selling_price)
                    VALUES %s
                    """,
                    order_details_values,
                )

            return Response(
                {
                    "status": "success",
                    "message": f"Successfully inserted {len(records)} records",
                }
            )

        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"status": "error", "message": f"Error inserting data: {str(e)}"},
                status=500,
            )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return Response(
            {
                "status": "error",
                "message": "An error occurred while processing your request.",
            },
            status=500,
        )