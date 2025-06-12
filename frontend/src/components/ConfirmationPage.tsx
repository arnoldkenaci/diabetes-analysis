import React from "react";
import { Box, Typography, Paper, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";

const ConfirmationPage = () => {
  const navigate = useNavigate();

  return (
    <Paper
      elevation={3}
      sx={{ p: 4, maxWidth: 600, mx: "auto", mt: 4, textAlign: "center" }}
    >
      <CheckCircleOutlineIcon
        sx={{ fontSize: 80, color: "success.main", mb: 2 }}
      />
      <Typography variant="h4" component="h1" gutterBottom>
        Thank You!
      </Typography>
      <Typography variant="body1" paragraph>
        Your information has been successfully submitted.
      </Typography>
      <Typography variant="body1" paragraph>
        You will receive an email with your results shortly.
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate("/")}
        >
          Return to Home
        </Button>
      </Box>
    </Paper>
  );
};

export default ConfirmationPage;
