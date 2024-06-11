delete_query = [
    "MATCH (i:Item) DETACH DELETE i;",
    "MATCH (c:Customer) DETACH DELETE c;",
    "MATCH (o:Order) DETACH DELETE o;"
]

create_query = """
CREATE 
(i1:Item {item_id: 1, category: "SUV", model: "Toyota RAV4", producer: "Toyota", price: 30000, color: "Silver"}),
(i2:Item {item_id: 2, category: "Sedan", model: "Honda Accord", producer: "Honda", price: 25000, color: "Black"}),
(i3:Item {item_id: 3, category: "Truck", model: "Ford F-150", producer: "Ford", price: 40000, color: "Blue"}),
(i4:Item {item_id: 4, category: "Electric", model: "Tesla Model 3", producer: "Tesla", price: 45000, color: "Red"}),
(i5:Item {item_id: 5, category: "Coupe", model: "Chevrolet Camaro", producer: "Chevrolet", price: 35000, color: "Yellow"}),
(i6:Item {item_id: 6, category: "Convertible", model: "BMW 4 Series", producer: "BMW", price: 50000, color: "White"}),
(i7:Item {item_id: 7, category: "Hatchback", model: "Volkswagen Golf", producer: "Volkswagen", price: 22000, color: "Green"}),
(i8:Item {item_id: 8, category: "Luxury", model: "Mercedes-Benz S-Class", producer: "Mercedes-Benz", price: 80000, color: "Black"}),
(i9:Item {item_id: 9, category: "Sports", model: "Porsche 911", producer: "Porsche", price: 100000, color: "Silver"}),

(c1:Customer {customer_id: 1, name: "John", surname: "Smith", phones: [123456789, 987654321], address: "123 Main St, Anytown, USA"}),
(c2:Customer {customer_id: 2, name: "Emma", surname: "Johnson", phones: [555555555, 777777777], address: "456 Oak St, Othertown, USA"}),
(c3:Customer {customer_id: 3, name: "Michael", surname: "Williams", phones: [333333333, 666666666], address: "789 Elm St, Thistown, USA"}),
(c4:Customer {customer_id: 4, name: "Sophia", surname: "Brown", phones: [888888888, 999999999], address: "101 Pine St, Anothertown, USA"}),
(c5:Customer {customer_id: 5, name: "Liam", surname: "Jones", phones: [111111111, 222222222], address: "135 Cedar St, Lasttown, USA"}),
(c6:Customer {customer_id: 6, name: "Olivia", surname: "Miller", phones: [444444444], address: "246 Birch St, Nexttown, USA"}),

(o1:Order {order_id: 201514, date: "2015-04-15"}),
(o2:Order {order_id: 201515, date: "2015-04-16"}),
(o3:Order {order_id: 201516, date: "2015-04-17"}),
(o4:Order {order_id: 201517, date: "2015-04-18"}),
(o5:Order {order_id: 201518, date: "2015-04-19"})
"""

# Use the MATCH to find the customer and order nodes based on their customer_id and order_id
bought_query = """
MATCH (c:Customer {customer_id: $customer_id}), (o:Order {order_id: $order_id})
MERGE (c)-[:BOUGHT]->(o)
"""

# Used to establish a relationship between an order node and an item node
contains_query = """
MATCH (o:Order {order_id: $order_id}), (i:Item {item_id: $item_id})
MERGE (o)-[:CONTAINS]->(i)
"""

# Used to establish a relationship between a customer and an item to represent a viewing action
view_query = """
MATCH (c:Customer {customer_id: $customer_id}), (i:Item {item_id: $item_id})
MERGE (c)-[:VIEW]->(i)
"""

# Updates the total_sum property of an order node based on the prices of the items contained in the order
update_total_sum_query = """
MATCH (o:Order {order_id: $order_id})
WITH o, [(o)-[:CONTAINS]->(i:Item) | i.price] AS prices
WITH o, reduce(total = 0, price IN prices | total + price) AS new_total_sum
SET o.total_sum = new_total_sum;
"""
