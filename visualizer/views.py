from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import pandas as pd
import logging


logger = logging.getLogger(__name__)


@api_view(["GET"])
def line_chart_monthly_sales_volume(request):
    """
    API endpoint that returns sales volume based on optional filters.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT o.date_of_sale, o.delivery_status, od.quantity_sold, o.platform_id, p.category, cad.state
                FROM orders as o 
                INNER JOIN order_details od ON o.id = od.order_id
                INNER JOIN product p ON od.product_id = p.id
                INNER JOIN customer_address_details cad ON o.customer_address_details_id = cad.id""",
            )
            order_data = cursor.fetchall()

        # Retrieve optional filters from query parameters
        filters = {
            "sales_date": request.query_params.get("date_range", None),
            "product_category": request.query_params.get("product_category", None),
            "delivery_status": request.query_params.get("delivery_status", None),
            "platform_id": request.query_params.get("platform_id", None),
            "state": request.query_params.get("state", None),
        }
        # Start with the full DataFrame
        filtered_data = pd.DataFrame(
            order_data,
            columns=[
                "date_of_sale",
                "delivery_status",
                "quantity_sold",
                "platform_id",
                "category",
                "state",
            ],
        )
        filtered_data["date_of_sale"] = pd.to_datetime(filtered_data["date_of_sale"])

        # Apply filters if provided
        if filters["sales_date"]:
            try:
                start_date, end_date = filters["sales_date"].split(",")
                filtered_data = filtered_data[
                    (filtered_data["date_of_sale"] >= start_date)
                    & (filtered_data["date_of_sale"] <= end_date)
                ]
            except ValueError:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid date range format. Use 'start_date,end_date'.",
                    },
                    status=400,
                )

        for key in ["product_category", "delivery_status", "platform_id", "state"]:
            if filters[key]:
                filtered_data = filtered_data[filtered_data[key] == int(filters[key])]

        monthly_sales = (
            filtered_data.groupby(filtered_data["date_of_sale"].dt.strftime("%Y-%m"))[
                "quantity_sold"
            ]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "date_of_sale": "month",
                    "quantity_sold": "total_sales_quantity",
                }
            )
        )

        # Sort by month to ensure chronological order
        monthly_sales = monthly_sales.sort_values("month")

        # Return the filtered results
        return Response(
            {
                "status": "success",
                "data": {
                    "labels": monthly_sales["month"].tolist(),
                    "values": monthly_sales["total_sales_quantity"].tolist(),
                },
            }
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


@api_view(["GET"])
def bar_chart_monthly_revenue(request):
    """
    API endpoint that returns revenue based on optional filters.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT o.date_of_sale, o.delivery_status, od.selling_price, o.platform_id, p.category, cad.state
                FROM orders as o 
                INNER JOIN order_details od ON o.id = od.order_id
                INNER JOIN product p ON od.product_id = p.id
                INNER JOIN customer_address_details cad ON o.customer_address_details_id = cad.id""",
            )
            order_data = cursor.fetchall()

        # Retrieve optional filters from query parameters
        filters = {
            "sales_date": request.query_params.get("date_range", None),
            "product_category": request.query_params.get("product_category", None),
            "delivery_status": request.query_params.get("delivery_status", None),
            "platform_id": request.query_params.get("platform_id", None),
            "state": request.query_params.get("state", None),
        }

        # Start with the full DataFrame
        filtered_data = pd.DataFrame(
            order_data,
            columns=[
                "date_of_sale",
                "delivery_status",
                "selling_price",
                "platform_id",
                "category",
                "state",
            ],
        )
        filtered_data["date_of_sale"] = pd.to_datetime(filtered_data["date_of_sale"])

        # Apply filters if provided
        if filters["sales_date"]:
            try:
                start_date, end_date = filters["sales_date"].split(",")
                filtered_data = filtered_data[
                    (filtered_data["date_of_sale"] >= start_date)
                    & (filtered_data["date_of_sale"] <= end_date)
                ]
            except ValueError:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid date range format. Use 'start_date,end_date'.",
                    },
                    status=400,
                )

        for key in ["product_category", "delivery_status", "platform_id", "state"]:
            if filters[key]:
                filtered_data = filtered_data[filtered_data[key] == int(filters[key])]

        monthly_sales = (
            filtered_data.groupby(filtered_data["date_of_sale"].dt.strftime("%Y-%m"))[
                "selling_price"
            ]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "date_of_sale": "month",
                    "selling_price": "total_sales_value",
                }
            )
        )

        # Sort by month to ensure chronological order
        monthly_sales = monthly_sales.sort_values("month")

        # Return the filtered results
        return Response(
            {
                "status": "success",
                "data": {
                    "labels": monthly_sales["month"].tolist(),
                    "values": monthly_sales["total_sales_value"].tolist(),
                },
            }
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


@api_view(["GET"])
def orders_summary(request):
    """
    API endpoint that returns revenue based on optional filters.
    """
    try:
        # Retrieve optional filters from query parameters
        filters = {
            "sales_date": request.query_params.get("date_range", None),
            "product_category": request.query_params.get("product_category", None),
            "delivery_status": request.query_params.get("delivery_status", None),
            "platform": request.query_params.get("platform", None),
            "state": request.query_params.get("state", None),
        }

        # Start with the full DataFrame
        filtered_data = pd.DataFrame(
            [],
            columns=[
                "sales_date",
                "product_category",
                "delivery_status",
                "platform",
                "state",
            ],
        )

        # Apply filters if provided
        if filters["sales_date"]:
            try:
                start_date, end_date = filters["sales_date"].split(",")
                filtered_data = filtered_data[
                    (filtered_data["sales_date"] >= start_date)
                    & (filtered_data["sales_date"] <= end_date)
                ]
            except ValueError:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid date range format. Use 'start_date,end_date'.",
                    },
                    status=400,
                )

        for key in ["product_category", "delivery_status", "platform", "state"]:
            if filters[key]:
                filtered_data = filtered_data[filtered_data[key] == filters[key]]

        # Return the filtered results
        return Response(
            {"status": "success", "data": filtered_data.to_dict(orient="records")}
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
