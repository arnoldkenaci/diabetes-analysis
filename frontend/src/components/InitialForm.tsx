import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Paper,
  Grid,
  Alert,
} from "@mui/material";
import { createInitialUserWithRecord } from "../services/api";
import axios from "axios";

const steps = ["Personal Information", "Health Information"];

const InitialForm = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    firstName: "John",
    lastName: "Doe",
    email: "arnold.kenaci1@gmail.com",
    gender: "male",
    pregnancies: "0",
    glucose: "120",
    bloodPressure: "80",
    skinThickness: "20",
    insulin: "100",
    bmi: "25.0",
    diabetesPedigree: "0.5",
    age: "30",
  });
  const navigate = useNavigate();

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const userData = {
        name: formData.firstName,
        surname: formData.lastName,
        email: formData.email,
      };

      const recordData = {
        pregnancies:
          formData.gender === "female" ? Number(formData.pregnancies) : null,
        glucose: Number(formData.glucose),
        blood_pressure: Number(formData.bloodPressure),
        skin_thickness: Number(formData.skinThickness),
        insulin: Number(formData.insulin),
        bmi: Number(formData.bmi),
        diabetes_pedigree: Number(formData.diabetesPedigree),
        age: Number(formData.age),
      };

      await createInitialUserWithRecord(userData, recordData);
      navigate("/confirmation");
    } catch (error) {
      console.error("Error submitting form:", error);
      setError(
        axios.isAxiosError(error)
          ? error.response?.data?.detail ||
              "An error occurred while submitting the form"
          : "An unexpected error occurred while submitting the form"
      );
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box component="form" sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl component="fieldset">
                  <FormLabel component="legend">Gender</FormLabel>
                  <RadioGroup
                    name="gender"
                    value={formData.gender}
                    onChange={handleInputChange}
                  >
                    <FormControlLabel
                      value="female"
                      control={<Radio />}
                      label="Female"
                    />
                    <FormControlLabel
                      value="male"
                      control={<Radio />}
                      label="Male"
                    />
                  </RadioGroup>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        );
      case 1:
        return (
          <Box component="form" sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              {formData.gender === "female" && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Number of Pregnancies"
                    name="pregnancies"
                    type="number"
                    value={formData.pregnancies}
                    onChange={handleInputChange}
                    inputProps={{ min: 0 }}
                    helperText="Number of times pregnant"
                  />
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Glucose Level"
                  name="glucose"
                  type="number"
                  value={formData.glucose}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0 }}
                  helperText="Plasma glucose concentration (mg/dL)"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Blood Pressure"
                  name="bloodPressure"
                  type="number"
                  value={formData.bloodPressure}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0 }}
                  helperText="Diastolic blood pressure (mm Hg)"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Skin Thickness"
                  name="skinThickness"
                  type="number"
                  value={formData.skinThickness}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0 }}
                  helperText="Triceps skin fold thickness (mm)"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Insulin Level"
                  name="insulin"
                  type="number"
                  value={formData.insulin}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0 }}
                  helperText="2-Hour serum insulin (mu U/ml)"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="BMI"
                  name="bmi"
                  type="number"
                  value={formData.bmi}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0, step: 0.1 }}
                  helperText="Body mass index (weight in kg/(height in m)^2)"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Diabetes Pedigree Function"
                  name="diabetesPedigree"
                  type="number"
                  value={formData.diabetesPedigree}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0, step: 0.001 }}
                  helperText="Diabetes pedigree function"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Age"
                  name="age"
                  type="number"
                  value={formData.age}
                  onChange={handleInputChange}
                  required
                  inputProps={{ min: 0 }}
                  helperText="Age in years"
                />
              </Grid>
            </Grid>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: "auto", mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Diabetes Assessment
      </Typography>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {renderStepContent(activeStep)}
      <Box sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        {activeStep === steps.length - 1 ? (
          <Button variant="contained" color="primary" onClick={handleSubmit}>
            Submit
          </Button>
        ) : (
          <Button variant="contained" color="primary" onClick={handleNext}>
            Next
          </Button>
        )}
      </Box>
    </Paper>
  );
};

export default InitialForm;
