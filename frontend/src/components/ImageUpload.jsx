import { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { CameraIcon, PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline';

const ImageUpload = ({ onImageSelected }) => {
  const [showWebcam, setShowWebcam] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      onImageSelected(file);
    }
  };

  const capturePhoto = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], `capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
          setSelectedFile(file);
          setPreview(imageSrc);
          setShowWebcam(false);
          onImageSelected(file);
        });
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreview(null);
    setShowWebcam(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!preview && !showWebcam && (
        <div className="flex flex-col space-y-4">
          <button
            onClick={() => fileInputRef.current.click()}
            className="flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors"
          >
            <PhotoIcon className="h-8 w-8 mr-2 text-gray-400" />
            <span className="text-lg text-gray-600">Choose Image from Device</span>
          </button>

          <button
            onClick={() => setShowWebcam(true)}
            className="flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors"
          >
            <CameraIcon className="h-8 w-8 mr-2 text-gray-400" />
            <span className="text-lg text-gray-600">Take Photo with Camera</span>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      )}

      {showWebcam && !preview && (
        <div className="relative">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            className="w-full rounded-lg"
            videoConstraints={{
              facingMode: "user"
            }}
          />
          <div className="flex justify-center space-x-4 mt-4">
            <button
              onClick={capturePhoto}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Capture Photo
            </button>
            <button
              onClick={() => setShowWebcam(false)}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {preview && (
        <div className="relative">
          <img src={preview} alt="Selected" className="w-full rounded-lg shadow-lg" />
          <button
            onClick={clearSelection}
            className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-full hover:bg-red-700"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
