def is_phone_valid(phone):
    digits = "".join([c for c in phone if c.isdigit()])
    if len(digits) != 10: return False
    
    # Prevent all same digits
    if len(set(digits)) == 1: return False
    
    # Starts with 6, 7, 8, or 9
    if int(digits[0]) not in [6, 7, 8, 9]: return False
    
    return True

print(f"9999999999: {is_phone_valid('9999999999')}")
print(f"1234567890: {is_phone_valid('1234567890')}")
print(f"9876543210: {is_phone_valid('9876543210')}")
