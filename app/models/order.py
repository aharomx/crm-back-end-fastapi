from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Order(BaseModel):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con cliente (obligatorio)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", foreign_keys=[client_id], back_populates="orders")
    
    # Relación con cotización (opcional)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    quote = relationship("Quote", foreign_keys=[quote_id])
    
    # Usuario que crea el pedido
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    
    # Datos del pedido
    order_number = Column(String(50), nullable=False, unique=True)
    order_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime, nullable=True)
    
    # Estado y prioridad
    status = Column(String(50), default="draft")  # draft, confirmed, in_progress, shipped, delivered, cancelled
    priority = Column(String(50), default="medium")  # low, medium, high
    
    # Totales
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Notas y dirección de envío
    notes = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    
    # Relación con items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(BaseModel):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con pedido
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="items")
    
    # Datos del item
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Referencia al item de cotización (opcional)
    quote_item_id = Column(Integer, nullable=True)