from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Platform
import pandas as pd
import logging


logger = logging.getLogger(__name__)


@api_view(["GET"])
def line_chart_monthly_sales_volume(request):
    """
    API endpoint that returns sales volume based on optional filters.
    """
    try:
        platform_objs = Platform.objects.filter(name="Flipkart")

        print(
            "platforms_filteredplatforms_filtered",
            [platform.name for platform in platform_objs],
        )

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


@api_view(["GET"])
def bar_chart_monthly_revenue(request):
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
