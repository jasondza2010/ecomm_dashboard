from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import pandas as pd
import logging


logger = logging.getLogger(__name__)


def build_filter_conditions(filters):
    """Helper function to build WHERE conditions and params from filters"""
    where_conditions = []
    params = []

    if filters["sales_date"]:
        try:
            start_date, end_date = filters["sales_date"].split(",")
            where_conditions.extend(["date_of_sale >= %s", "date_of_sale <= %s"])
            params.extend([start_date, end_date])
        except ValueError:
            raise ValueError(
                "Invalid date range format. Use 'start_date,end_date' in YYYY-MM-DD format."
            )

    filter_mappings = {
        "category": ("category = %s", str),
        "delivery_status": ("delivery_status = %s", str),
        "platform_id": ("platform_id = %s", int),
        "state": ("state = %s", str),
    }

    for key, (condition, type_cast) in filter_mappings.items():
        if filters[key]:
            where_conditions.append(condition)
            params.append(type_cast(filters[key]))

    return where_conditions, params


def get_filtered_data(query, filters):
    """Helper function to execute query and return filtered data"""
    where_conditions, params = build_filter_conditions(filters)

    if where_conditions:
        query += " WHERE " + " AND ".join(where_conditions)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def process_monthly_data(data, date_col, value_col, columns):
    """Helper function to process monthly aggregations"""
    df = pd.DataFrame(data, columns=columns)
    df[date_col] = pd.to_datetime(df[date_col])

    monthly_data = (
        df.groupby(df[date_col].dt.strftime("%Y-%m"))[value_col]
        .sum()
        .reset_index()
        .rename(columns={date_col: "month"})
        .sort_values("month")
    )

    return {
        "labels": monthly_data["month"].tolist(),
        "values": monthly_data[value_col].tolist(),
    }

@api_view(["GET"])
def line_chart_monthly_sales_volume(request):
    """API endpoint that returns sales volume based on optional filters."""
    try:
        filters = {
            "sales_date": request.query_params.get("date_range"),
            "category": request.query_params.get("product_category"),
            "delivery_status": request.query_params.get("delivery_status"),
            "platform_id": request.query_params.get("platform_id"),
            "state": request.query_params.get("state"),
        }

        query = "SELECT date_of_sale, quantity_sold FROM mv_order_details"
        data = get_filtered_data(query, filters)

        result = process_monthly_data(
            data=data,
            date_col="date_of_sale",
            value_col="quantity_sold",
            columns=["date_of_sale", "quantity_sold"],
        )

        return Response({"status": "success", "data": result})

    except ValueError as ve:
        return Response({"status": "error", "message": str(ve)}, status=400)
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
    """API endpoint that returns revenue based on optional filters."""
    try:
        filters = {
            "sales_date": request.query_params.get("date_range"),
            "category": request.query_params.get("product_category"),
            "delivery_status": request.query_params.get("delivery_status"),
            "platform_id": request.query_params.get("platform_id"),
            "state": request.query_params.get("state"),
        }

        query = "SELECT date_of_sale, selling_price FROM mv_order_details"
        data = get_filtered_data(query, filters)

        result = process_monthly_data(
            data=data,
            date_col="date_of_sale",
            value_col="selling_price",
            columns=["date_of_sale", "selling_price"],
        )

        return Response({"status": "success", "data": result})

    except ValueError as ve:
        return Response({"status": "error", "message": str(ve)}, status=400)
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
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT o.delivery_status, od.selling_price, od.quantity_sold
                FROM orders as o 
                INNER JOIN order_details od ON o.id = od.order_id
                INNER JOIN product p ON od.product_id = p.id
                INNER JOIN customer_address_details cad ON o.customer_address_details_id = cad.id""",
            )
            order_data = cursor.fetchall()

        # Start with the full DataFrame
        filtered_data = pd.DataFrame(
            order_data,
            columns=["delivery_status", "selling_price", "quantity_sold"],
        )
        total_orders = filtered_data.shape[0]
        total_revenue = filtered_data["selling_price"].sum()
        total_products_sold = filtered_data["quantity_sold"].sum()
        canceled_order_percentage = (
            filtered_data[filtered_data["delivery_status"] == "Cancelled"].shape[0]
            / total_orders
            * 100
        )

        return Response(
            {
                "status": "success",
                "data": {
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "total_products_sold": total_products_sold,
                    "canceled_order_percentage": canceled_order_percentage,
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
