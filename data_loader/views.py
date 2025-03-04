from rest_framework.decorators import api_view
from rest_framework.response import Response
from ecomm_dashboard.visualizer.models import Platform
import pandas as pd
import logging
import requests
import io
import numpy as np

logger = logging.getLogger(__name__)


@api_view(["POST"])
def extract_order_data(request):
    """
    API endpoint that returns sales volume based on optional filters.
    """
    try:
        csv_drive_urls = request.data.get(
            "urls", []
        )  # Get the list of URLs from the request

        csv_dataframes = []  # Initialize a list to hold data from all CSVs

        for drive_url in csv_drive_urls:
            try:
                # Extract file ID from Google Drive URL
                google_file_id = drive_url.split("/d/")[1].split("/")[0]
                download_url = f"https://drive.google.com/uc?id={google_file_id}"

                # Download CSV content using requests with SSL verification disabled
                response = requests.get(download_url, verify=False)
                response.raise_for_status()  # Raise exception for bad status codes

                # Read CSV from the response content
                csv_data = pd.read_csv(io.StringIO(response.text))
                csv_dataframes.append(csv_data)
            except Exception as e:
                return Response(
                    {"status": "error", "message": f"Error reading CSV file: {str(e)}"},
                    status=400,
                )

        # Combine all data into a single DataFrame
        merged_dataframe = pd.concat(csv_dataframes, ignore_index=True)
        merged_dataframe = merged_dataframe.replace({np.nan: None})

        # Return the filtered results
        return Response(
            {"status": "success", "data": merged_dataframe.to_dict(orient="records")}
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