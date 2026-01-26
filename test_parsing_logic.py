import re
import unittest

class TestRegistrationParsing(unittest.TestCase):
    def setUp(self):
        # Copied from analyze_registrations_count.py
        self.product_pattern = re.compile(
            r'(.*?)\s*\(Amount:\s*([\d\.]+).*?, Quantity:\s*(\d+)(?:, Registration Type:\s*([^,)]+))?.*?\)'
        )

    def test_parsing_cases(self):
        test_cases = [
            # Standard case
            ("WACYPAA 27 Registration (Amount: 20.00 USD, Quantity: 1)", 
             "WACYPAA 27 Registration", 20, 1, "Unspecified"),
            
            # With Registration Type
            ("WACYPAA 27 Registration (Amount: 35.00 USD, Quantity: 2, Registration Type: Scholarship)", 
             "WACYPAA 27 Registration", 35, 2, "Scholarship"),
            
            # 0.00 Amount
            ("Scholarship Donation (Amount: 0.00 USD, Quantity: 1)", 
             "Scholarship Donation", 0, 1, "Unspecified"),
            
            # Decimal Amount
            ("Merch (Amount: 12.50 USD, Quantity: 1)", 
             "Merch", 12.5, 1, "Unspecified"),
            
            # Weird spacing
            (" Weird Spaced Registration  (Amount:  50.00   USD, Quantity:  1 )", 
             "Weird Spaced Registration", 50, 1, "Unspecified"),
            
            # No Registration Type but comma
            ("Product (Amount: 10.00 USD, Quantity: 1, some other field: value)", 
             "Product", 10, 1, "Unspecified"),

            # Test 25.00
            ("WACYPAA 27 Registration (Amount: 25.00 USD, Quantity: 1)",
             "WACYPAA 27 Registration", 25, 1, "Unspecified")
        ]
        
        for input_str, exp_name, exp_price, exp_qty, exp_type in test_cases:
            with self.subTest(input_str=input_str):
                match = self.product_pattern.search(input_str)
                self.assertTrue(match, f"No match for '{input_str}'")
                
                name = match.group(1).strip()
                price_str = match.group(2)
                qty_str = match.group(3)
                # Group 4 is Registration Type
                reg_type = match.group(4).strip() if match.group(4) else "Unspecified"
                
                try:
                    price_val = float(price_str)
                    if price_val.is_integer():
                        price_val = int(price_val)
                except ValueError:
                    price_val = -1
                    
                qty = int(qty_str)
                
                self.assertEqual(name, exp_name)
                self.assertEqual(price_val, exp_price)
                self.assertEqual(qty, exp_qty)
                self.assertEqual(reg_type, exp_type)

if __name__ == "__main__":
    unittest.main()
