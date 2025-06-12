import { useSearchParams } from "react-router-dom";
import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { getHealthAssessment } from "../services/api";
import InitialForm from "../components/InitialForm";

const Dashboard = () => {
  const [searchParams] = useSearchParams();
  const assessmentId = searchParams.get("assessment_id");
  const existingUser = searchParams.get("existing_user") === "true";

  const {
    data: assessmentData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["healthAssessment", assessmentId],
    queryFn: () => getHealthAssessment(Number(assessmentId)),
    enabled: !!assessmentId,
  });

  // If no assessment ID, show the initial form
  if (!assessmentId) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ flexGrow: 1, py: 4 }}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Typography variant="h4" component="h1" gutterBottom>
                Welcome to Diabetes Risk Assessment
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Please fill out the form below to get started with your
                assessment. This will help us analyze your risk factors and
                provide personalized recommendations.
              </Typography>
              {existingUser && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Welcome back! We found your existing account. Your new
                  assessment will be added to your records.
                </Alert>
              )}
            </Grid>
            <Grid item xs={12}>
              <InitialForm />
            </Grid>
          </Grid>
        </Box>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "60vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">
          {error instanceof Error ? error.message : "An error occurred"}
        </Alert>
      </Container>
    );
  }

  if (!assessmentData) return null;

  return (
    <Container maxWidth="lg">
      <Box sx={{ flexGrow: 1, py: 4 }}>
        <Grid container spacing={4}>
          <Grid item xs={12}>
            <Typography variant="h4" component="h1" gutterBottom>
              Your Health Assessment Results
            </Typography>
            {existingUser && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Your assessment has been added to your existing account.
              </Alert>
            )}
          </Grid>

          {/* Health Assessment Section */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk Assessment
                </Typography>
                <Typography variant="body1" paragraph>
                  {assessmentData.recommendations.risk_assessment}
                </Typography>
                <Typography variant="subtitle1" color="primary">
                  Risk Level: {assessmentData.risk_level.toUpperCase()}
                </Typography>
                <Typography variant="subtitle2" color="text.secondary">
                  Risk Score: {(assessmentData.risk_score * 100).toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                <List>
                  {assessmentData.recommendations.recommendations.map(
                    (rec: string, index: number) => (
                      <ListItem key={index}>
                        <ListItemText primary={rec} />
                      </ListItem>
                    )
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Preventive Measures */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Preventive Measures
                </Typography>
                <List>
                  {assessmentData.recommendations.preventive_measures.map(
                    (measure: string, index: number) => (
                      <ListItem key={index}>
                        <ListItemText primary={measure} />
                      </ListItem>
                    )
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;
