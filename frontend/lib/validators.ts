// TEMPORARY PLACEHOLDER: Owned by in3 (Tharani Jayaprakash).
// This validators module is kept here temporarily for local authentication forms to function,
// and should be replaced/removed upon merging in3's branch to avoid conflicts.

export function validateEmail(email: string): { isValid: boolean; error?: string } {
  if (!email) {
    return { isValid: false, error: "Email is required" };
  }
  const normalized = email.trim().toLowerCase();
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!pattern.test(normalized)) {
    return { isValid: false, error: "Invalid email format" };
  }
  return { isValid: true };
}

export function validatePassword(password: string): { isValid: boolean; error?: string } {
  if (!password) {
    return { isValid: false, error: "Password is required" };
  }
  if (password.length < 8) {
    return { isValid: false, error: "Password must be at least 8 characters long" };
  }
  if (!/[a-zA-Z]/.test(password)) {
    return { isValid: false, error: "Password must contain at least one letter" };
  }
  if (!/\d/.test(password)) {
    return { isValid: false, error: "Password must contain at least one number" };
  }
  return { isValid: true };
}

export function validatePhone(phone: string): { isValid: boolean; error?: string } {
  if (!phone) {
    return { isValid: false, error: "Phone number is required" };
  }
  const clean = phone.trim();
  const pattern = /^[6-9]\d{9}$/;
  if (!pattern.test(clean)) {
    return { isValid: false, error: "Phone must be a valid 10-digit Indian mobile number" };
  }
  return { isValid: true };
}

export function validatePincode(pincode: string): { isValid: boolean; error?: string } {
  if (!pincode) {
    return { isValid: false, error: "Pincode is required" };
  }
  const clean = pincode.trim();
  const pattern = /^\d{6}$/;
  if (!pattern.test(clean)) {
    return { isValid: false, error: "Pincode must be a 6-digit numeric code" };
  }
  return { isValid: true };
}
