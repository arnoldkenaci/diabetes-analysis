import React from "react";
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import type { DiabetesRecord } from "../types/diabetes";

interface UserAttempt {
  id: number;
  filename: string;
  records_count: number;
  status: "success" | "failed" | "processing";
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

const UserAttempts: React.FC = () => {
  const {
    data: attempts,
    isLoading,
    error,
  } = useQuery<UserAttempt[]>({
    queryKey: ["userAttempts"],
    queryFn: () => api.get("/api/v1/attempts").then((res) => res.data),
  });

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="200px"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="200px"
      >
        <Alert severity="error">Failed to load attempts</Alert>
      </Box>
    );
  }

  if (!attempts || attempts.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Uploads
          </Typography>
          <Alert severity="info">No upload attempts found</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Uploads
        </Typography>
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Filename</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Records</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Completed</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {attempts.slice(0, 5).map((attempt) => (
                <TableRow key={attempt.id}>
                  <TableCell>{attempt.filename}</TableCell>
                  <TableCell>
                    {attempt.status === "success" ? (
                      <Alert severity="success" sx={{ py: 0 }}>
                        Success
                      </Alert>
                    ) : attempt.status === "failed" ? (
                      <Alert severity="error" sx={{ py: 0 }}>
                        {attempt.error_message}
                      </Alert>
                    ) : (
                      <Alert severity="info" sx={{ py: 0 }}>
                        Processing
                      </Alert>
                    )}
                  </TableCell>
                  <TableCell>{attempt.records_count}</TableCell>
                  <TableCell>
                    {new Date(attempt.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    {attempt.completed_at
                      ? new Date(attempt.completed_at).toLocaleString()
                      : "-"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default UserAttempts;
