import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiAlertOctagon, FiArrowLeft } from 'react-icons/fi';
import './NotFoundPage.css';

/**
 * NotFoundPage - 404 Error catch-all page
 * Custom galactic lost themed page returning the user to the admin area
 */
const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="not-found-page">
      <div className="space-overlay">
        <div className="star-field" />
      </div>
      <motion.div
        className="not-found-card"
        initial={{ opacity: 0, scale: 0.9, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <div className="error-badge">
          <FiAlertOctagon />
          <span>Error 404</span>
        </div>
        <h1 className="lost-title">Lost in Orbit</h1>
        <p className="lost-description">
          The quadrant you are attempting to access does not exist or has been relocated outside the observable GALXY.
        </p>
        <button className="lost-action-btn" onClick={() => navigate('/admin/products')}>
          <FiArrowLeft />
          <span>Return to Dashboard</span>
        </button>
      </motion.div>
    </div>
  );
};

export default NotFoundPage;
