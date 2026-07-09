import { useState, useCallback } from 'react';
import adminProductApi from '../services/api/adminProductApi';
import { validateImageFile } from '../utils/helpers';
import toast from 'react-hot-toast';

// Flag to toggle between mock data and real API
const USE_MOCK = false;

/**
 * useImageManager - Custom hook for managing product images
 * Handles upload, delete, thumbnail selection, and drag & drop
 * @param {string} productId - Product ID to manage images for
 * @param {Array} initialImages - Initial images array
 */
const useImageManager = (productId, initialImages = []) => {
  const [images, setImages] = useState(initialImages);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  // True right after the thumbnail image was deleted and other images remain,
  // so the UI can prompt the admin to pick a replacement immediately instead
  // of silently leaving the product with no thumbnail.
  const [needsThumbnailPick, setNeedsThumbnailPick] = useState(false);

  /**
   * Upload images to the server
   * @param {FileList|Array} files - Files to upload
   */
  const uploadImages = useCallback(
    async (files) => {
      const fileArray = Array.from(files);

      // Validate all files first
      const validationErrors = [];
      fileArray.forEach((file) => {
        const validation = validateImageFile(file);
        if (!validation.valid) {
          validationErrors.push(`${file.name}: ${validation.error}`);
        }
      });

      if (validationErrors.length > 0) {
        validationErrors.forEach((err) => toast.error(err));
        return;
      }

      // Check max images limit
      if (images.length + fileArray.length > 8) {
        toast.error(`Maximum 8 images allowed. You can add ${8 - images.length} more.`);
        return;
      }

      setUploading(true);
      setUploadProgress(0);

      try {
        if (USE_MOCK) {
          // Simulate upload with progress
          for (let i = 0; i <= 100; i += 10) {
            await new Promise((resolve) => setTimeout(resolve, 100));
            setUploadProgress(i);
          }

          // Generate mock uploaded images
          const newImages = fileArray.map((file, index) => ({
            _id: `img_new_${Date.now()}_${index}`,
            url: URL.createObjectURL(file),
            isThumbnail: images.length === 0 && index === 0,
            name: file.name,
          }));

          setImages((prev) => [...prev, ...newImages]);
          toast.success(`${fileArray.length} image(s) uploaded successfully`);
        } else {
          const formData = new FormData();
          fileArray.forEach((file) => formData.append('images', file));

          const result = await adminProductApi.uploadImages(productId, formData, (event) => {
            const progress = Math.round((event.loaded * 100) / event.total);
            setUploadProgress(progress);
          });

          if (result.success) {
            setImages(result.data.images);
            toast.success(`${fileArray.length} image(s) uploaded successfully`);
          }
        }
      } catch (err) {
        toast.error('Failed to upload images');
      } finally {
        setUploading(false);
        setUploadProgress(0);
      }
    },
    [productId, images]
  );

  /**
   * Delete an image
   * @param {string} imageId - Image ID to delete
   */
  const deleteImage = useCallback(
    async (imageId) => {
      const deletedImage = images.find((img) => img._id === imageId);
      const wasThumbnail = !!deletedImage?.isThumbnail;

      try {
        if (USE_MOCK) {
          await new Promise((resolve) => setTimeout(resolve, 300));
          setImages((prev) => prev.filter((img) => img._id !== imageId));
          toast.success('Image deleted successfully');
        } else {
          await adminProductApi.deleteImage(productId, imageId);
          setImages((prev) => prev.filter((img) => img._id !== imageId));
          toast.success('Image deleted successfully');
        }

        const remaining = images.filter((img) => img._id !== imageId);
        if (wasThumbnail && remaining.length > 0) {
          setNeedsThumbnailPick(true);
        }
      } catch (err) {
        toast.error('Failed to delete image');
      }
      setDeleteConfirm(null);
    },
    [productId, images]
  );

  /**
   * Set image as thumbnail
   * @param {string} imageId - Image ID to set as thumbnail
   */
  const setThumbnail = useCallback(
    async (imageId) => {
      try {
        if (USE_MOCK) {
          await new Promise((resolve) => setTimeout(resolve, 200));
          setImages((prev) =>
            prev.map((img) => ({
              ...img,
              isThumbnail: img._id === imageId,
            }))
          );
          toast.success('Thumbnail updated');
        } else {
          await adminProductApi.setThumbnail(productId, imageId);
          setImages((prev) =>
            prev.map((img) => ({
              ...img,
              isThumbnail: img._id === imageId,
            }))
          );
          toast.success('Thumbnail updated');
        }
        setNeedsThumbnailPick(false);
      } catch (err) {
        toast.error('Failed to set thumbnail');
      }
    },
    [productId]
  );

  /**
   * Show delete confirmation for an image
   */
  const confirmDelete = useCallback((imageId) => {
    setDeleteConfirm(imageId);
  }, []);

  /**
   * Cancel delete confirmation
   */
  const cancelDelete = useCallback(() => {
    setDeleteConfirm(null);
  }, []);

  return {
    images,
    setImages,
    uploading,
    uploadProgress,
    uploadImages,
    deleteImage,
    setThumbnail,
    deleteConfirm,
    confirmDelete,
    cancelDelete,
    needsThumbnailPick,
  };
};

export default useImageManager;
