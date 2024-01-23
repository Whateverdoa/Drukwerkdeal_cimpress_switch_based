import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Union, Optional

from models.vila_model.vila_esko_model import OrderInfo, Delivery, Contact
from models.vila_model.vila_esko_model import Contact

def read_xml_file(file_path: Path) -> Path:
    with open(file_path, 'r') as file:
        return file.read()

# Function to parse XML and convert to OrderInfo dataclass
def parse_xml_to_order_info(xml_content: str) -> OrderInfo:
    # Parse the XML content
    root = ET.fromstring(xml_content)

    width_in_mm = float(root.find('.//Custom-Width').text) * 10
    height_in_mm = float(root.find('.//Custom-Height').text) * 10    

    # Extract Winding value
    winding = int(root.find('.//Unwind-Direction').text.split()[-1])  # Extracting last numeric part

    # Swap Width and Height if Winding is 3, 4, 7, or 8
    if winding in [3, 4, 7, 8]:
        width_in_mm, height_in_mm = height_in_mm, width_in_mm

    # Convert the results to strings and replace dots with commas
    width_in_mm_string = str(width_in_mm).replace('.', ',')
    height_in_mm_string = str(height_in_mm).replace('.', ',')

    def price_per_1000(totalprice, quantity):
        if quantity == 0:
            return 0.0
        else:
            return round((totalprice / quantity) * 1000, 2)


    # Extract information for OrderInfo
    description = root.find('.//orderId').text
    item_order_id = root.find('.//itemId').text
    # promised_date = root.find('.//promisedArrivalDate').text
    expectedShipTime_date = root.find('.//expectedShipTime').text
    promised_date = str(expectedShipTime_date)[:10]

    # Find the expectedCarrierServiceName element and get its text
    Shipment = root.find('.//expectedCarrierServiceName').text

    quantity = int(root.find('.//quantity').text)
    # Extract UnitPrice and round to two decimal places
    unit_price = round(float(root.find('.//fulfillerPrice/amount').text), 2)
    shape = root.find('.//Shape-Roll-Stickers').text
    radius = int(root.find('.//Corner-Finishing-Radius').text)
    substrate = root.find('.//Material-Stickers').text
    adhesive = root.find('.//Adhesion-Stickers').text

    PricePer1000=price_per_1000(unit_price, quantity)

    # Extract Contact information
    contact_element = root.find('.//destinationAddress')

    email_element = contact_element.find('.//email')
    if email_element is not None:
        Email = email_element.text
    else:
        Email = "no@email.com" # or some default value, or handle the absence of email differently

    contact = Contact(
        LastName=contact_element.find('.//lastName').text,
        FirstName=contact_element.find('.//firstName').text,
        Initials="",  # Placeholder
        Title="",  # Placeholder
        PhoneNumber=contact_element.find('.//phone').text,
        FaxNumber="",  # Placeholder
        GSMNumber="",  # Placeholder
        Email=Email,
        Function=""  # Placeholder
    )

    # Extract Delivery information
    delivery = Delivery(
        Type="",  # Placeholder
        Comment="",  # Placeholder
        AddressId="",  # Placeholder
        ExpectedDate=promised_date
    )

    # Create and return OrderInfo instance
    order_info = OrderInfo(

        Description=description,
        ReferenceAtCustomer=item_order_id,
        Delivery=promised_date,
        Shipment_method=Shipment,  # Placeholder
        OrderQuantity=quantity,
        Quantity_per_roll="",  # Placeholder
        Core="",  # Placeholder	
        UnitPrice=PricePer1000,
        
        # SupplierId=root.find('.//merchantId').text,
        SupplierId='Drukwerkdeal',
        Name=contact_element.find('.//lastName').text,
        Street=contact_element.find('.//street1').text,
        Country=contact_element.find('.//country').text,
        PostalCode=contact_element.find('.//postalCode').text,
        City=contact_element.find('.//city').text,
        Contacts=[contact],
        Width=width_in_mm_string,
        Height=height_in_mm_string,
        Shape=shape,
        Winding=winding,
        Radius=radius,
        Premium_White="N",  # Placeholder
        Substrate=substrate,
        Adhesive=adhesive,
        LineComment1=f"{item_order_id}" # Optional field, set to None
    )

    return order_info


# Function to convert OrderInfo instance to JSON
def order_info_to_json(order_info: OrderInfo) -> str:
    return json.dumps(asdict(order_info), indent=4)

# file_path = 'E:\SWITCH\DWD_CERM_CONN\F6D9E9C26E/Cimpress_F6D9E9C26E.xml'  # Replace with your XML file path
# xml_content = read_xml_file(file_path)
# order_info = parse_xml_to_order_info(xml_content)
# json_output = order_info_to_json(order_info)
# print(json_output)

