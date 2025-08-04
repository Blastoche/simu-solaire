# -*- coding: utf-8 -*-
"""
Calculateur d'indicateurs économiques pour installations solaires
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging

from config.tariffs import TARIFFS

logger = logging.getLogger(__name__)

def analyze(
    pv_production: Dict,
    consumption: Dict,
    investment_cost: Optional[float] = None,
    tariffs: Optional[Dict] = None,
    system_power_kw: Optional[float] = None
) -> Dict:
    """
    Analyse économique complète de l'installation solaire
    
    Args:
        pv_production: Résultats de production PV
        consumption: Résultats de consommation
        investment_cost: Coût d'investissement (€)
        tariffs: Tarifs personnalisés (sinon utilise config)
        system_power_kw: Puissance installée pour calcul automatique du coût
    
    Returns:
        Dict avec tous les indicateurs économiques
    """
    try:
        # Utilisation des tarifs par défaut si non fournis
        if tariffs is None:
            tariffs = TARIFFS
        
        # Extraction des séries horaires
        production_hourly = pv_production.get('hourly_production_kw', pd.Series())
        consumption_hourly = consumption.get('consumption_kw', pd.Series())
        
        if len(production_hourly) == 0 or len(consumption_hourly) == 0:
            raise ValueError("Données de production ou consommation manquantes")
        
        # Alignement des séries temporelles
        production_hourly, consumption_hourly = _align_time_series(
            production_hourly, consumption_hourly
        )
        
        # Calculs des flux énergétiques
        energy_flows = _calculate_energy_flows(production_hourly, consumption_hourly)
        
        # Estimation automatique du coût d'investissement si nécessaire
        if investment_cost is None:
            if system_power_kw:
                investment_cost = system_power_kw * 2500  # 2500€/kWc moyenne
            else:
                # Estimation basée sur la production
                estimated_power = pv_production.get('annual_yield_kwh', 0) / 1200
                investment_cost = estimated_power * 2500
        
        # Calculs économiques
        financial_metrics = _calculate_financial_metrics(
            energy_flows, investment_cost, tariffs
        )
        
        # Calcul des aides et subventions
        subsidies = _calculate_subsidies(system_power_kw or estimated_power, tariffs)
        
        # Compilation des résultats
        results = {
            **energy_flows,
            **financial_metrics,
            **subsidies,
            'investment_cost_euro': float(investment_cost),
            'system_power_kw': system_power_kw or estimated_power
        }
        
        logger.info(f"Analyse économique terminée - ROI: {results.get('roi_years', 'N/A'):.1f} ans")
        return results
        
    except Exception as e:
        logger.error(f"Erreur analyse économique: {str(e)}")
        return _get_default_economic_results()

def _align_time_series(production: pd.Series, consumption: pd.Series) -> tuple:
    """
    Aligne deux séries temporelles et les redimensionne si nécessaire
    """
    # Si les longueurs diffèrent, on prend la plus courte
    min_length = min(len(production), len(consumption))
    
    if min_length == 0:
        raise ValueError("Séries temporelles vides")
    
    production_aligned = production.iloc[:min_length]
    consumption_aligned = consumption.iloc[:min_length]
    
    # Vérification et nettoyage des valeurs
    production_aligned = production_aligned.fillna(0).clip(lower=0)
    consumption_aligned = consumption_aligned.fillna(0).clip(lower=0)
    
    return production_aligned, consumption_aligned

def _calculate_energy_flows(production: pd.Series, consumption: pd.Series) -> Dict:
    """
    Calcule les flux énergétiques horaires
    """
    # Autoconsommation instantanée
    autoconsumption = np.minimum(production, consumption)
    
    # Surplus injecté au réseau
    surplus = np.maximum(production - consumption, 0)
    
    # Déficit prélevé du réseau
    deficit = np.maximum(consumption - production, 0)
    
    # Calcul des taux
    total_production = production.sum()
    total_consumption = consumption.sum()
    total_autoconsumption = autoconsumption.sum()
    
    autoconsumption_rate = total_autoconsumption / total_production if total_production > 0 else 0
    autonomy_rate = total_autoconsumption / total_consumption if total_consumption > 0 else 0
    
    return {
        'autoconsumption_kwh': float(total_autoconsumption),
        'surplus_kwh': float(surplus.sum()),
        'deficit_kwh': float(deficit.sum()),
        'autoconsumption_rate': float(autoconsumption_rate),
        'autonomy_rate': float(autonomy_rate),
        'total_production_kwh': float(total_production),
        'total_consumption_kwh': float(total_consumption)
    }

def _calculate_financial_metrics(energy_flows: Dict, investment_cost: float, tariffs: Dict) -> Dict:
    """
    Calcule les indicateurs financiers
    """
    # Prix de l'électricité
    purchase_price = tariffs['electricity']['purchase']  # €/kWh
    
    # Prix de vente (injection) - utilise le tarif le plus bas par défaut
    sell_prices = tariffs['electricity']['sell']
    sell_price = min(sell_prices.values()) if isinstance(sell_prices, dict) else 0.04
    
    # Économies annuelles
    autoconsumption_savings = energy_flows['autoconsumption_kwh'] * purchase_price
    injection_revenue = energy_flows['surplus_kwh'] * sell_price
    annual_savings = autoconsumption_savings + injection_revenue
    
    # Coût évité (ce qu'on aurait payé sans solaire)
    avoided_cost = energy_flows['autoconsumption_kwh'] * purchase_price
    
    # ROI simple
    roi_years = investment_cost / annual_savings if annual_savings > 0 else float('inf')
    
    # Calcul sur 25 ans avec dégradation
    cashflow_25_years = _calculate_long_term_cashflow(
        annual_savings, investment_cost, degradation_rate=0.005
    )
    
    return {
        'annual_savings': float(annual_savings),
        'autoconsumption_savings': float(autoconsumption_savings),
        'injection_revenue': float(injection_revenue),
        'avoided_cost': float(avoided_cost),
        'roi_years': float(roi_years),
        'net_present_value_25y': float(cashflow_25_years['npv']),
        'total_savings_25y': float(cashflow_25_years['total_savings']),
        'purchase_price_kwh': purchase_price,
        'sell_price_kwh': sell_price
    }

def _calculate_long_term_cashflow(
    annual_savings: float,
    investment_cost: float,
    years: int = 25,
    degradation_rate: float = 0.005,
    discount_rate: float = 0.03
) -> Dict:
    """
    Calcule les flux de trésorerie sur le long terme
    """
    cashflows = []
    total_savings = 0
    
    for year in range(years):
        # Dégradation progressive de la production
        degradation_factor = (1 - degradation_rate) ** year
        yearly_savings = annual_savings * degradation_factor
        
        # Actualisation des flux
        discounted_savings = yearly_savings / (1 + discount_rate) ** year
        cashflows.append(discounted_savings)
        total_savings += yearly_savings
    
    # Valeur actuelle nette
    npv = sum(cashflows) - investment_cost
    
    return {
        'npv': npv,
        'total_savings': total_savings,
        'payback_time': _calculate_payback_time(annual_savings, investment_cost, degradation_rate)
    }

def _calculate_payback_time(
    annual_savings: float,
    investment_cost: float,
    degradation_rate: float = 0.005
) -> float:
    """
    Calcule le temps de retour sur investissement avec dégradation
    """
    if annual_savings <= 0:
        return float('inf')
    
    cumulative_savings = 0
    year = 0
    
    while cumulative_savings < investment_cost and year < 50:
        year += 1
        degradation_factor = (1 - degradation_rate) ** (year - 1)
        yearly_savings = annual_savings * degradation_factor
        cumulative_savings += yearly_savings
    
    return float(year)

def _calculate_subsidies(system_power_kw: float, tariffs: Dict) -> Dict:
    """
    Calcule les aides financières disponibles
    """
    subsidies_config = tariffs.get('subsidies', {})
    
    # Prime à l'autoconsommation
    autoconsumption_bonus = 0
    if 'autoconsommation' in subsidies_config:
        bonus_rates = subsidies_config['autoconsommation']
        
        if system_power_kw <= 3:
            autoconsumption_bonus = bonus_rates.get('≤3kWc', 0) * system_power_kw
        elif system_power_kw <= 9:
            autoconsumption_bonus = bonus_rates.get('3-9kWc', 0) * system_power_kw
        else:
            autoconsumption_bonus = bonus_rates.get('9-36kWc', 0) * min(system_power_kw, 36)
    
    # TVA réduite
    tva_reduction = 0
    if 'tva_reduced' in subsidies_config and system_power_kw <= 3:
        # Estimation: 10% de réduction sur 20% de TVA = 2% du coût HT
        estimated_cost_ht = system_power_kw * 2083  # 2500€ TTC = 2083€ HT
        tva_reduction = estimated_cost_ht * 0.02
    
    # Autres aides locales (à personnaliser selon région)
    regional_bonus = 0  # À implémenter selon la localisation
    
    total_subsidies = autoconsumption_bonus + tva_reduction + regional_bonus
    
    return {
        'subsidies_euro': float(total_subsidies),
        'autoconsumption_bonus': float(autoconsumption_bonus),
        'tva_reduction': float(tva_reduction),
        'regional_bonus': float(regional_bonus)
    }

def _get_default_economic_results() -> Dict:
    """
    Retourne des résultats par défaut en cas d'erreur
    """
    return {
        'autoconsumption_kwh': 0.0,
        'surplus_kwh': 0.0,
        'deficit_kwh': 0.0,
        'autoconsumption_rate': 0.0,
        'autonomy_rate': 0.0,
        'annual_savings': 0.0,
        'roi_years': float('inf'),
        'subsidies_euro': 0.0,
        'investment_cost_euro': 0.0,
        'error': 'Calcul économique échoué'
    }

def generate_economic_report(results: Dict) -> str:
    """
    Génère un rapport économique textuel
    """
    report = f"""
    📊 ANALYSE ÉCONOMIQUE DE L'INSTALLATION SOLAIRE
    
    💰 INVESTISSEMENT
    • Coût total: {results.get('investment_cost_euro', 0):,.0f} €
    • Aides financières: {results.get('subsidies_euro', 0):,.0f} €
    • Coût net: {results.get('investment_cost_euro', 0) - results.get('subsidies_euro', 0):,.0f} €
    
    ⚡ BILAN ÉNERGÉTIQUE ANNUEL
    • Production: {results.get('total_production_kwh', 0):,.0f} kWh
    • Consommation: {results.get('total_consumption_kwh', 0):,.0f} kWh
    • Autoconsommation: {results.get('autoconsumption_kwh', 0):,.0f} kWh
    • Surplus injecté: {results.get('surplus_kwh', 0):,.0f} kWh
    
    📈 INDICATEURS CLÉS
    • Taux d'autoconsommation: {results.get('autoconsumption_rate', 0):.1%}
    • Taux d'autonomie: {results.get('autonomy_rate', 0):.1%}
    • Économies annuelles: {results.get('annual_savings', 0):,.0f} €
    • Retour sur investissement: {results.get('roi_years', float('inf')):.1f} ans
    
    🏆 RENTABILITÉ SUR 25 ANS
    • Économies totales: {results.get('total_savings_25y', 0):,.0f} €
    • Valeur actuelle nette: {results.get('net_present_value_25y', 0):,.0f} €
    """
    
    return report
