# models.py - COMPLETE VERSION
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # admin, manager, accountant, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_number = db.Column(db.String(50), unique=True, nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    weight = db.Column(db.Float)
    status = db.Column(db.String(20), default='Active')  # Active, Sick, Deceased, Sold
    pen_number = db.Column(db.String(20))
    health_status = db.Column(db.String(20), default='Good')  # Good, Sick, Recovering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Animal {self.tag_number} - {self.breed}>'

class Breeding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sow_id = db.Column(db.String(50), nullable=False)  # Animal tag or ID
    boar_id = db.Column(db.String(50), nullable=False)
    breeding_date = db.Column(db.Date, nullable=False)
    expected_farrowing = db.Column(db.Date)
    actual_farrowing = db.Column(db.Date)
    litter_size = db.Column(db.Integer)
    method = db.Column(db.String(50), default='natural')  # natural, artificial
    pregnant = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Breeding {self.sow_id} x {self.boar_id}>'

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.String(50), nullable=False)
    treatment_type = db.Column(db.String(100), nullable=False)  # Vaccination, Medication, Checkup
    diagnosis = db.Column(db.String(200))
    medication = db.Column(db.String(200))
    dosage = db.Column(db.String(100))
    cost = db.Column(db.Float, default=0.0)
    vet_name = db.Column(db.String(100))
    treatment_date = db.Column(db.Date, nullable=False)
    next_checkup = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicalRecord {self.animal_id} - {self.treatment_type}>'

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_type = db.Column(db.String(100), nullable=False)  # Starter, Grower, Finisher, Premix
    quantity_kg = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float)
    supplier = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    min_level = db.Column(db.Float, default=10.0)  # Minimum stock level
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feed {self.feed_type} - {self.quantity_kg}kg>'

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)  # Live Animal, Meat, Breeding Stock
    quantity = db.Column(db.Integer, default=1)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')  # Paid, Pending, Partial
    payment_method = db.Column(db.String(50))  # Cash, M-Pesa, Bank
    invoice_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sale {self.customer_name} - Ksh{self.total_amount}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    customer_type = db.Column(db.String(50))  # Pig buyer, Breeder, Meat processor, Wholesaler
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    preferred_product = db.Column(db.String(100))
    delivery_preference = db.Column(db.String(50), default='pickup')  # pickup, delivery
    credit_limit = db.Column(db.Float, default=0.0)
    outstanding_balance = db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    last_purchase_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # Farm Manager, Assistant, Vet, etc.
    department = db.Column(db.String(100))
    salary = db.Column(db.Float, nullable=False)
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, On Leave
    emergency_contact = db.Column(db.String(20))
    certifications = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Staff {self.name} - {self.role}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.String(100))  # Staff name or ID
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Completed
    priority = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    category = db.Column(db.String(50))  # Feeding, Cleaning, Medical, Maintenance
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    completed_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title} - {self.status}>'

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Feed, Medicine, Equipment, Services
    contact_person = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    website = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    reliability_score = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(50))
    delivery_lead_time = db.Column(db.Integer)  # days
    total_spent = db.Column(db.Float, default=0.0)
    last_order_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Feed, Medicine, Equipment, Supply
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')  # kg, liters, pieces, boxes
    unit_price = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float)
    supplier = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    min_level = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(100))  # Storage location
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inventory {self.item_name} - {self.quantity}{self.unit}>'

# Note: FinancialTransaction model can be added later for expense tracking