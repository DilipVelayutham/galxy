/**
 * Client-side validation module for GALXY Module 1.
 * Matches backend validation rules and error messages exactly.
 */

export interface ValidationResult {
  isValid: boolean;
  error: string;
  value?: string;
}

export function validateEmail(email: string): ValidationResult {
  if (!email) {
    return { isValid: false, error: "Email is required" };
  }
  const cleanEmail = email.trim();
  // Standard RFC 5322 regex matching backend
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(cleanEmail)) {
    return { isValid: false, error: "Invalid email format" };
  }
  return { isValid: true, error: "", value: cleanEmail.toLowerCase() };
}

export function validatePassword(password: string): ValidationResult {
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
  return { isValid: true, error: "" };
}

export function validatePhone(phone: string): ValidationResult {
  if (!phone) {
    return { isValid: false, error: "Phone number is required" };
  }
  const cleanPhone = phone.trim();
  // 10-digit Indian mobile format (starts with 6, 7, 8, or 9)
  const phoneRegex = /^[6-9]\d{9}$/;
  if (!phoneRegex.test(cleanPhone)) {
    return { isValid: false, error: "Phone number must be a valid 10-digit Indian mobile number" };
  }
  return { isValid: true, error: "", value: cleanPhone };
}

export function validatePincode(pincode: string): ValidationResult {
  if (!pincode) {
    return { isValid: false, error: "Pincode is required" };
  }
  const cleanPincode = pincode.trim();
  // 6-digit numeric pincode
  const pincodeRegex = /^\d{6}$/;
  if (!pincodeRegex.test(cleanPincode)) {
    return { isValid: false, error: "Pincode must be exactly 6 digits" };
  }
  return { isValid: true, error: "", value: cleanPincode };
}
