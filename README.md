
# Ecomm Dashboard

A project for loading and retrieving bulk order data across all customer eCommerce dashboards.


## API Reference

#### Get monthly sales volume

```http
  GET /visualizer/monthly_sales_volume
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `sales_date` | `string` | *Optional*. |
| `product_category` | `string` | *Optional*. |
| `delivery_status` | `string` | *Optional*. |
| `platform_id` | `int` | *Optional*. |
| `state` | `string` | *Optional*. |

#### Get monthly sales revenue

```http
  GET /visualizer/monthly_revenue
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `sales_date` | `string` | *Optional*. |
| `product_category` | `string` | *Optional*. |
| `delivery_status` | `string` | *Optional*. |
| `platform_id` | `int` | *Optional*. |
| `state` | `string` | *Optional*. |


#### Upload orders from Ecommerce platforms

```http
  POST /data_loader/extract_order_data
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `urls` | `list` | *Required*. |
