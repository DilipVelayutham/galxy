import React, { useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiUploadCloud,
  FiX,
  FiTrash2,
  FiStar,
  FiCheck,
  FiImage,
  FiAlertTriangle,
} from 'react-icons/fi';
import useImageManager from '../../../../hooks/useImageManager';
import './ImageManager.css';

/**
 * ImageManager - Modal component for managing product images
 * Features drag & drop upload, preview, delete, and thumbnail selection
 */
const ImageManager = ({ product, onClose }) => {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const {
    images,
    uploading,
    uploadProgress,
    uploadImages,
    deleteImage,
    setThumbnail,
    deleteConfirm,
    confirmDelete,
    cancelDelete,
    needsThumbnailPick,
  } = useImageManager(product?._id, product?.images || []);

  // Handle file input change
  const handleFileSelect = (e) => {
    if (e.target.files?.length) {
      uploadImages(e.target.files);
      e.target.value = ''; // Reset input
    }
  };

  // Drag & Drop handlers
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files?.length) {
        uploadImages(files);
      }
    },
    [uploadImages]
  );

  return (
    <motion.div
      className="image-manager-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="image-manager-modal"
        initial={{ opacity: 0, scale: 0.9, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 30 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="image-manager-header">
          <div>
            <h2 className="image-manager-title">Manage Images</h2>
            <p className="image-manager-subtitle">{product?.title}</p>
          </div>
          <button className="image-manager-close" onClick={onClose} aria-label="Close">
            <FiX />
          </button>
        </div>

        {/* Upload Zone */}
        <div
          className={`upload-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => !uploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={handleFileSelect}
            className="upload-input"
          />

          {uploading ? (
            <div className="upload-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
              <span className="progress-text">Uploading... {uploadProgress}%</span>
            </div>
          ) : (
            <>
              <FiUploadCloud className="upload-icon" />
              <p className="upload-text">
                <strong>Click to upload</strong> or drag and drop
              </p>
              <p className="upload-hint">JPG, PNG, WebP, GIF up to 5MB · Max 8 images</p>
            </>
          )}
        </div>

        {/* Image count */}
        <div className="image-count">
          <FiImage />
          <span>{images.length} / 8 images</span>
        </div>

        {/* Thumbnail replacement prompt -- shown right after the thumbnail
            image was deleted, so the admin picks a new one immediately
            instead of the product silently ending up with no thumbnail. */}
        {needsThumbnailPick && (
          <div className="thumbnail-pick-banner">
            <FiAlertTriangle />
            <span>
              The thumbnail image was removed. Click the star on an image below to set a new thumbnail.
            </span>
          </div>
        )}

        {/* Image Grid */}
        <div className="image-grid">
          <AnimatePresence>
            {images.map((image) => (
              <motion.div
                key={image._id}
                className={`image-card ${image.isThumbnail ? 'is-thumbnail' : ''}`}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                layout
              >
                <img src={image.url} alt="Product" className="image-preview" />

                {/* Thumbnail indicator */}
                {image.isThumbnail && (
                  <div className="thumbnail-badge">
                    <FiStar />
                    <span>Thumbnail</span>
                  </div>
                )}

                {/* Action buttons */}
                <div className="image-actions">
                  {!image.isThumbnail && (
                    <button
                      className="img-action-btn set-thumb"
                      onClick={() => setThumbnail(image._id)}
                      title="Set as thumbnail"
                    >
                      <FiStar />
                    </button>
                  )}
                  <button
                    className="img-action-btn delete-img"
                    onClick={() => confirmDelete(image._id)}
                    title="Delete image"
                  >
                    <FiTrash2 />
                  </button>
                </div>

                {/* Delete Confirmation */}
                <AnimatePresence>
                  {deleteConfirm === image._id && (
                    <motion.div
                      className="delete-confirm-overlay"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <FiAlertTriangle className="delete-warn-icon" />
                      <p>Delete this image?</p>
                      <div className="delete-confirm-btns">
                        <button className="dc-btn dc-cancel" onClick={cancelDelete}>
                          Cancel
                        </button>
                        <button className="dc-btn dc-delete" onClick={() => deleteImage(image._id)}>
                          <FiCheck /> Delete
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Empty State */}
        {images.length === 0 && (
          <div className="images-empty">
            <FiImage className="images-empty-icon" />
            <p>No images uploaded yet</p>
            <span>Upload product images to showcase your product</span>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default ImageManager;
