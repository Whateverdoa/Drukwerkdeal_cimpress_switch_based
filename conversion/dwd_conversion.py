import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict, fields
from pathlib import Path
from typing import List, Union, Optional
import unicodedata

from models.vila_model.vila_esko_model import OrderInfo, Delivery, Contact
from models.vila_model.vila_esko_model import Contact


def verwijder_speciale_tekens(input_string: str) -> str:
    """
    Removes special characters and diacritic marks from the input string
    by normalizing the unicode characters and replacing certain non-ASCII characters.

    Args:
        input_string (str): The string from which special characters need to be removed.

    Returns:
        str: The string with special characters and diacritic marks removed.
    """
    # Mapping of non-ASCII characters to their closest ASCII equivalents
    char_mapping = {
        'ø': 'o',
        'å': 'a',
        'Ø': 'O',
        'Å': 'A',
        '/': ' ',
        '.': '',
        # Add more mappings as needed
    }

    # Normalize the string and remove diacritic marks
    normalized_string = unicodedata.normalize('NFKD', input_string)
    no_diacritics = "".join([c for c in normalized_string if not unicodedata.combining(c)])

    # Replace non-ASCII characters using the mapping
    result = "".join([char_mapping.get(c, c) for c in no_diacritics])
    return result

def read_xml_file(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_missing_fields(json_output: str, dataclass_type: type) -> list:
    """
    Function to get all fields in a dataclass that are not present in a JSON string.

    :param json_output: JSON string.
    :param dataclass_type: Type of the dataclass.
    :return: List of field names that are missing in the JSON.
    """
    # Load JSON as a dictionary
    json_dict = json.loads(json_output)

    # Get all field names from the dataclass
    model_fields = {field.name for field in fields(dataclass_type)}

    # Get all keys from json dictionary
    json_keys = set(json_dict.keys())

    # Find fields that are in the model but not in the JSON
    missing_fields = model_fields - json_keys

    return list(missing_fields)


def price_per_1000(totalprice, quantity):
    if quantity == 0:
        return 0.0
    else:
        return round((totalprice / quantity) * 1000, 2)


# Function to parse XML and convert to OrderInfo dataclass
def safe_get_element_text(root, tag, default=None):
    element = root.find(tag)
    return element.text if element is not None else default


def parse_xml_to_order_info(xml_content: str) -> Optional[OrderInfo]:
    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Mathematical fields
    width_in_mm = float(safe_get_element_text(root, './/Custom-Width', default="0")) * 10
    height_in_mm = float(safe_get_element_text(root, './/Custom-Height', default="0")) * 10
    winding = int(safe_get_element_text(root, './/Unwind-Direction', default="0").split()[-1])
    if winding in [3, 4, 7, 8]:
        width_in_mm, height_in_mm = height_in_mm, width_in_mm

    # Textual fields
    description = safe_get_element_text(root, './/orderId', default='error')
    item_order_id = safe_get_element_text(root, './/itemId', default='')
    expectedShipTime_date = safe_get_element_text(root, './/expectedShipTime', default='')
    promised_date = str(expectedShipTime_date)[:10] if expectedShipTime_date else ''
    shipment = safe_get_element_text(root, './/expectedCarrierServiceName', default='')
    quantity = int(safe_get_element_text(root, './/quantity', default="0"))
    unit_price = round(float(safe_get_element_text(root, './/fulfillerPrice/amount', default="0")), 2)
    shape = safe_get_element_text(root, './/Shape-Roll-Stickers', default='')
    radius = int(safe_get_element_text(root, './/Corner-Finishing-Radius', default="0"))
    substrate = safe_get_element_text(root, './/Material-Stickers', default='')
    adhesive = safe_get_element_text(root, './/Adhesion-Stickers', default='')
    PricePer1000 = price_per_1000(unit_price, quantity)

    # Contact fields
    contact_element = root.find('.//destinationAddress')
    if contact_element is None:
        return None
    else:
        email_element = safe_get_element_text(root, './/email', default='no@email.com')
        contact = Contact(
            LastName=verwijder_speciale_tekens(safe_get_element_text(contact_element, './/lastName', default='')),
            FirstName=verwijder_speciale_tekens(safe_get_element_text(contact_element, './/firstName', default='')),
            Initials="",  # Placeholder
            Title="",  # Placeholder
            PhoneNumber=safe_get_element_text(contact_element, './/phone', default=''),
            FaxNumber="",  # Placeholder
            GSMNumber="",  # Placeholder
            Email=email_element,
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
        Shipment_method=shipment,  # Placeholder
        OrderQuantity=quantity,
        Quantity_per_roll="",  # Placeholder
        Core="",  # Placeholder
        UnitPrice=PricePer1000,
        SupplierId='Drukwerkdeal',
        Name=safe_get_element_text(root, './/name', default=''),
        Street=verwijder_speciale_tekens(safe_get_element_text(contact_element, './/street1', default='')),
        Country=verwijder_speciale_tekens(safe_get_element_text(contact_element, './/country', default='')),
        PostalCode=safe_get_element_text(contact_element, './/postalCode', default=''),
        City=verwijder_speciale_tekens(safe_get_element_text(contact_element, './/city', default='')),
        Contacts=[contact],
        Width=str(width_in_mm).replace('.', ','),
        Height=str(height_in_mm).replace('.', ','),
        Shape=shape,
        Winding=winding,
        Radius=radius,
        Premium_White="N",  # Placeholder
        Substrate=substrate,
        Adhesive=adhesive,
        LineComment1=f"{item_order_id}"  # Optional field
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