from dataclasses import dataclass, field
from typing import List, Union, Optional


# Define helloprint_converted_dataclass Contact dataclass
@dataclass
class Contact:
    LastName: str
    FirstName: str
    Initials: str
    Title: str
    PhoneNumber: str
    FaxNumber: str
    GSMNumber: str
    Email: str
    Function: str


# Define helloprint_converted_dataclass Delivery dataclass
@dataclass
class Delivery:
    Type: str
    Comment: str
    AddressId: str
    ExpectedDate: str


# Define the main OrderInfo dataclass
@dataclass
class OrderInfo:

    Description: str
    ReferenceAtCustomer: str
    Delivery: str  # due date
    Shipment_method: str
    OrderQuantity: Union[int, str]
    Quantity_per_roll: str
    Core: str
    UnitPrice: float
    SupplierId: str
    Name: str
    Street: str
    Country: str
    PostalCode: str
    City: str
    Contacts: List[Contact]

    Width: str
    Height: str

    Shape: str  # def for conversion
    Winding: int  # def for conversion
    Radius: int  # def for conversion
    Premium_White: str  # def for conversion if pantone contains white
    Substrate: str
    Adhesive: str


    LineComment1: Optional[str] = field(default=None)