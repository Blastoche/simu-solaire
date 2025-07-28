# -*- coding: utf-8 -*-
"""
Interaction avec la base de données des simulations
"""
from sqlalchemy import create_engine, Column, Float, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
from config import DATABASE_URL  # À définir dans config/database.py

Base = declarative_base()

class PVSimulationResult(Base):
    __tablename__ = 'pv_simulation_results'

    id = Column(String, primary_key=True)  # hash des paramètres
    location = Column(JSON)
    system = Column(JSON)
    hourly_production = Column(JSON)  # Stockage en JSON pour simplicité
    annual_yield = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_simulation(self, params_hash: str, params: dict, results: dict):
        """Sauvegarde une simulation en base"""
        session = self.Session()
        try:
            record = PVSimulationResult(
                id=params_hash,
                location=params["location"],
                system=params["system"],
                hourly_production=results["hourly"].to_dict(),
                annual_yield=results["annual_yield"]
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def get_simulation(self, params_hash: str) -> dict:
        """Récupère une simulation depuis la base"""
        session = self.Session()
        try:
            record = session.query(PVSimulationResult).filter_by(id=params_hash).first()
            if record:
                return {
                    "hourly": pd.Series(record.hourly_production),
                    "annual_yield": record.annual_yield,
                    "cached": True
                }
        finally:
            session.close()
