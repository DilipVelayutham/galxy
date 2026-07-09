import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiAlertCircle } from 'react-icons/fi';
import './ValidationErrors.css';

/**
 * ValidationErrors - Displays inline validation error messages
 * Uses Framer Motion for smooth entry/exit animations
 * @param {string} message - Error message to display
 * @param {boolean} show - Whether to show the error
 */
const ValidationErrors = ({ message, show = true }) => {
  return (
    <AnimatePresence mode="wait">
      {show && message && (
        <motion.div
          className="validation-error"
          initial={{ opacity: 0, y: -8, height: 0 }}
          animate={{ opacity: 1, y: 0, height: 'auto' }}
          exit={{ opacity: 0, y: -8, height: 0 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          <FiAlertCircle className="validation-error-icon" />
          <span className="validation-error-text">{message}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ValidationErrors;
