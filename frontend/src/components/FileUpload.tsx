import React, { useState } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  Alert,
} from "@mui/material";
import { Upload as UploadIcon } from "@mui/icons-material";
import { uploadDataset } from "../services/api";

interface FileUploadProps {
  onUploadSuccess?: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith(".csv")) {
        setError("Please select a CSV file");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await uploadDataset(formData);
      setSuccess(`Successfully uploaded ${response.records_uploaded} records`);
      setFile(null);
      onUploadSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ p: 3, border: "1px dashed #ccc", borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Upload Dataset
      </Typography>

      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadIcon />}
          disabled={uploading}
        >
          Select File
          <input type="file" hidden accept=".csv" onChange={handleFileChange} />
        </Button>

        {file && <Typography variant="body2">Selected: {file.name}</Typography>}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Button
        variant="contained"
        color="primary"
        onClick={handleUpload}
        disabled={!file || uploading}
        sx={{ mt: 2 }}
      >
        {uploading ? (
          <>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            Uploading...
          </>
        ) : (
          "Upload"
        )}
      </Button>
    </Box>
  );
};
