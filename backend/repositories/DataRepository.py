
from datetime import datetime, date
from .Database import Database

class DataRepository:
    
    @staticmethod
    def setup_tables():
        """
        Controleer of tables bestaan - GEEN AANMAKEN omdat ze al bestaan
        """
        try:
            check_device = "SELECT COUNT(*) as count FROM Device LIMIT 1"
            result = Database.get_one_row(check_device)
            
            if result:
                print("✅ Database tables bestaan al")
                return True
            else:
                print("❌ Database tables niet gevonden")
                return False
                
        except Exception as e:
            print(f"❌ Database check error: {e}")
            return False
    
    @staticmethod
    def insert_test_data():
        """Insert test device als die niet bestaat"""
        try:
            # Check of device 1 bestaat
            check_device = "SELECT DeviceID FROM Device WHERE DeviceID = 1"
            device = Database.get_one_row(check_device)
            
            if not device:
                # Insert device 1
                sql_device = """
                INSERT INTO Device (DeviceID, Beschrijving, Actief_Sinds, Is_Actief) 
                VALUES (1, 'Smart Drink Device #1', %s, 1)
                """
                Database.execute_sql(sql_device, (datetime.now(),))
                print(" Test device aangemaakt")
            else:
                print(" Test device bestaat al")
            
        except Exception as e:
            print(f" Test data error: {e}")
    
    @staticmethod
    def save_drink_complete(device_id, drink_type, volume, temperatuur=None, vochtigheid=None):
        """
        AANGEPASTE VERSIE - Opslaan volgens jouw database schema
        """
        try:
            # volume_cola en volume_water
            volume_cola = volume if drink_type.lower() == 'cola' else 0
            volume_water = volume if drink_type.lower() == 'water' else 0
            
            # 1.meting in Historiek 
            sql_historiek = """
            INSERT INTO Historiek (DeviceID, DrankType, Tijdsstip, Volume_Cola, Volume_Water, Temperatuur, Vochtigheid) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            tijdstip = datetime.now()
            
            result = Database.execute_sql(sql_historiek, (
                device_id, 
                drink_type, 
                tijdstip, 
                volume_cola, 
                volume_water, 
                temperatuur, 
                vochtigheid
            ))
            
            if result:
                print(f" Historiek opgeslagen: {drink_type} {volume}ml")

                DataRepository.update_dagelijkse_samenvatting(device_id, tijdstip.date())
                
                return True
            else:
                print(" Fout bij opslaan in Historiek")
                return False
                
        except Exception as e:
            print(f" Database save error: {e}")
            return False
    
    @staticmethod
    def update_dagelijkse_samenvatting(device_id, datum):
        """
        AANGEPASTE VERSIE - Update volgens jouw schema
        """
        try:
            # 1. totale dag Historiek
            sql_totalen = """
            SELECT 
                COUNT(*) as totaal_metingen,
                SUM(CASE WHEN DrankType = 'cola' THEN 1 ELSE 0 END) as aantal_cola,
                SUM(CASE WHEN DrankType = 'water' THEN 1 ELSE 0 END) as aantal_water,
                SUM(Volume_Cola) as totaal_cola,
                SUM(Volume_Water) as totaal_water,
                AVG(Temperatuur) as gem_temperatuur,
                AVG(Vochtigheid) as gem_vochtigheid
            FROM Historiek 
            WHERE DeviceID = %s AND DATE(Tijdsstip) = %s
            """
            
            totalen = Database.get_one_row(sql_totalen, (device_id, datum))
            
            if totalen and totalen['totaal_metingen'] > 0:
                # 2. Check of bestaat
                check_sql = """
                SELECT Samenvatting_ID FROM Dagelijkse_Samenvatting 
                WHERE DeviceID = %s AND Datum = %s
                """
                bestaande = Database.get_one_row(check_sql, (device_id, datum))
                
                if bestaande:
                    # Update bestaande record
                    update_sql = """
                    UPDATE Dagelijkse_Samenvatting SET
                        Aantal_Cola = %s,
                        Aantal_Water = %s,
                        Volume_Cola = %s,
                        Volume_Water = %s,
                        Temperatuur = %s,
                        Vochtigheid = %s
                    WHERE DeviceID = %s AND Datum = %s
                    """
                    
                    params = (
                        totalen['aantal_cola'] or 0,
                        totalen['aantal_water'] or 0,
                        totalen['totaal_cola'] or 0,
                        totalen['totaal_water'] or 0,
                        totalen['gem_temperatuur'],
                        totalen['gem_vochtigheid'],
                        device_id,
                        datum
                    )
                else:
                    # Insert nieuwe record
                    update_sql = """
                    INSERT INTO Dagelijkse_Samenvatting 
                    (DeviceID, Datum, Aantal_Cola, Aantal_Water, Volume_Cola, Volume_Water, Temperatuur, Vochtigheid)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    params = (
                        device_id,
                        datum,
                        totalen['aantal_cola'] or 0,
                        totalen['aantal_water'] or 0,
                        totalen['totaal_cola'] or 0,
                        totalen['totaal_water'] or 0,
                        totalen['gem_temperatuur'],
                        totalen['gem_vochtigheid']
                    )
                
                result = Database.execute_sql(update_sql, params)
                
                if result:
                    print(f" Dagelijkse samenvatting updated voor {datum}")
                    return True
                else:
                    print(f" Fout bij update samenvatting voor {datum}")
                    return False
            else:
                print(f" Geen historiek gevonden voor {datum}")
                return False
                
        except Exception as e:
            print(f" Samenvatting update error: {e}")
            return False
    
    @staticmethod
    def read_samenvatting(device_id, datum):
        """
        AANGEPASTE VERSIE - Lees volgens jouw schema
        """
        try:
            sql_vandaag = """
            SELECT 
                ds.Aantal_Cola,
                ds.Aantal_Water,
                ds.Volume_Cola,
                ds.Volume_Water,
                ds.Temperatuur,
                ds.Vochtigheid
            FROM Dagelijkse_Samenvatting ds
            WHERE ds.DeviceID = %s AND ds.Datum = %s
            """
            
            samenvatting_vandaag = Database.get_one_row(sql_vandaag, (device_id, datum))
            
            dagen_achter_elkaar = DataRepository.bereken_dagen_achter_elkaar(device_id, datum)
            
            if samenvatting_vandaag:
                totaal_volume = (samenvatting_vandaag['Volume_Cola'] or 0) + (samenvatting_vandaag['Volume_Water'] or 0)
                totaal_keren = (samenvatting_vandaag['Aantal_Cola'] or 0) + (samenvatting_vandaag['Aantal_Water'] or 0)
                
                result = {
                    'totaal_volume_liters': float(totaal_volume) / 1000,  
                    'aantal_keren_gebruikt': int(totaal_keren),
                    'dagen_achter_elkaar': dagen_achter_elkaar,
                    'aantal_cola': int(samenvatting_vandaag['Aantal_Cola'] or 0),
                    'aantal_water': int(samenvatting_vandaag['Aantal_Water'] or 0),
                    'totaal_cola_ml': float(samenvatting_vandaag['Volume_Cola'] or 0),
                    'totaal_water_ml': float(samenvatting_vandaag['Volume_Water'] or 0),
                    'gemiddelde_temperatuur': float(samenvatting_vandaag['Temperatuur'] or 0),
                    'gemiddelde_vochtigheid': float(samenvatting_vandaag['Vochtigheid'] or 0),
                    'laatste_update': str(datum)
                }
            else:
                # Geen data voor vandaag
                result = {
                    'totaal_volume_liters': 0.0,
                    'aantal_keren_gebruikt': 0,
                    'dagen_achter_elkaar': dagen_achter_elkaar,
                    'aantal_cola': 0,
                    'aantal_water': 0,
                    'totaal_cola_ml': 0.0,
                    'totaal_water_ml': 0.0,
                    'gemiddelde_temperatuur': 0.0,
                    'gemiddelde_vochtigheid': 0.0,
                    'laatste_update': None
                }
            
            print(f" Samenvatting opgehaald voor {datum}: {result}")
            return result
            
        except Exception as e:
            print(f" Samenvatting lezen error: {e}")
            return {
                'totaal_volume_liters': 0.0,
                'aantal_keren_gebruikt': 0,
                'dagen_achter_elkaar': 0,
                'aantal_cola': 0,
                'aantal_water': 0,
                'totaal_cola_ml': 0.0,
                'totaal_water_ml': 0.0,
                'gemiddelde_temperatuur': 0.0,
                'gemiddelde_vochtigheid': 0.0,
                'laatste_update': None
            }
        
    @staticmethod
    def bereken_dagen_achter_elkaar(device_id, datum):
        try:
            sql_dagen = """
            SELECT DISTINCT DATE(Tijdsstip) as datum
            FROM Historiek
            WHERE DeviceID = %s 
            AND DATE(Tijdsstip) <= %s
            ORDER BY datum DESC
            """
            
            dagen_met_gebruik = Database.get_rows(sql_dagen, (device_id, datum))
            
            if not dagen_met_gebruik:
                return 0
            
            dagen_achter_elkaar = 0
            huidige_datum = datum
            
            for dag_row in dagen_met_gebruik:
                dag_datum = dag_row['datum']
                
                if dag_datum == huidige_datum:
                    dagen_achter_elkaar += 1

                    from datetime import timedelta
                    huidige_datum = huidige_datum - timedelta(days=1)
                else:
                    break
            #Dag is geskipt
            print(f" Streak berekening: {dagen_achter_elkaar} dagen voor device {device_id}")
            return dagen_achter_elkaar
            
        except Exception as e:
            print(f" Dagen achter elkaar berekening error: {e}")
            return 0
        
    @staticmethod
    def get_historiek(device_id, limit=50):
        try:
            sql = """
            SELECT 
                HistoriekID,
                DrankType,
                Volume_Cola,
                Volume_Water,
                Temperatuur,
                Vochtigheid,
                Tijdsstip
            FROM Historiek 
            WHERE DeviceID = %s 
            ORDER BY Tijdsstip DESC 
            LIMIT %s
            """
            
            historiek = Database.get_rows(sql, (device_id, limit))
            
            if historiek:
                # Convert datetime objects to strings en voeg totaal volume toe
                for meting in historiek:
                    if meting['Tijdsstip']:
                        meting['Tijdsstip'] = str(meting['Tijdsstip'])
                    
                    # Voeg totaal volume toe voor frontend
                    meting['Volume'] = (meting['Volume_Cola'] or 0) + (meting['Volume_Water'] or 0)
                
                return historiek
            else:
                return []
                
        except Exception as e:
            print(f" Historiek ophalen error: {e}")
            return []

#Test voor debug

    @staticmethod
    def test_database_functions():
        """Test alle database functies"""
        try:
            print("=== Database Functie Test ===")

            print("1. Test save_drink_complete...")
            success = DataRepository.save_drink_complete(1, 'water', 250.0, 22.0, 55.0)
            print(f"   Result: {' SUCCESS' if success else ' FAILED'}")
            
            print("2. Test read_samenvatting...")
            vandaag = date.today()
            samenvatting = DataRepository.read_samenvatting(1, vandaag)
            print(f"   Result: {samenvatting}")
            
            print("3. Test get_historiek...")
            historiek = DataRepository.get_historiek(1, 10)
            print(f"   Result: {len(historiek)} records")
            
            print("=== Test Voltooid ===")
            
        except Exception as e:
            print(f" Database test error: {e}")

    #Voor alles aan/uit te zetten (onder instructie)
    @staticmethod
    def get_device_status(device_id):
        """Haal huidige device status op"""
        try:
            sql = "SELECT Is_Actief FROM Device WHERE DeviceID = %s"
            result = Database.get_one_row(sql, (device_id,))
            return bool(result['Is_Actief']) if result else False
        except Exception as e:
            print(f" Device status error: {e}")
            return False

    @staticmethod
    def update_device_status(device_id, is_actief):
        """Update device status in database"""
        try:
            sql = "UPDATE Device SET Is_Actief = %s WHERE DeviceID = %s"
            result = Database.execute_sql(sql, (is_actief, device_id))
            if result:
                print(f" Device {device_id} status updated: {'ON' if is_actief else 'OFF'}")
                return True
            return False
        except Exception as e:
            print(f" Device status update error: {e}")
            return False

    @staticmethod
    def log_device_action(device_id, action, success):
        """Log device aan/uit acties voor security"""
        try:
            from datetime import datetime
            sql = """
            INSERT INTO Historiek (DeviceID, DrankType, Tijdsstip, Volume_Cola, Volume_Water, Temperatuur, Vochtigheid) 
            VALUES (%s, %s, %s, 0, 0, NULL, NULL)
            """
            # Gebruik DrankType field voor logging (tijdelijke oplossing)
            log_entry = f"DEVICE_{action}_{'SUCCESS' if success else 'FAILED'}"
            Database.execute_sql(sql, (device_id, log_entry, datetime.now()))
            print(f" Device action logged: {log_entry}")
        except Exception as e:
            print(f" Device logging error: {e}")


# Test script
if __name__ == "__main__":
    print("=== DataRepository Test ===")
    
    # Check tables
    if DataRepository.setup_tables():
        print(" Tables check OK")
        
        #  test data
        DataRepository.insert_test_data()
        
        # Run tests
        DataRepository.test_database_functions()
    else:
        print("❌ Tables check FAILED")