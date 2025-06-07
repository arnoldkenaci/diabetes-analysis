import React, { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Bar, Pie } from "react-chartjs-2";
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Divider,
} from "@mui/material";
import {
  Warning as WarningIcon,
  TrendingUp,
  TrendingDown,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";
import type { DiabetesRecord } from "../types/diabetes";
import type { AnalysisResult } from "../types/analysis";
import { api } from "../services/api";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const DashboardCharts: React.FC = () => {
  const [data, setData] = useState<DiabetesRecord[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dataResponse, analysisResponse] = await Promise.all([
          api.get<DiabetesRecord[]>("/api/v1/data"),
          api.get<AnalysisResult>("/api/v1/analyze"),
        ]);
        setData(dataResponse.data);
        setAnalysis(analysisResponse.data);
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch data");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
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
        minHeight="400px"
      >
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  // Calculate statistics
  const averageGlucose =
    data.reduce((acc, curr) => acc + curr.glucose, 0) / data.length;
  const averageBMI =
    data.reduce((acc, curr) => acc + curr.bmi, 0) / data.length;
  const averageAge =
    data.reduce((acc, curr) => acc + curr.age, 0) / data.length;
  const diabetesRate =
    (data.filter((r) => r.diabetes).length / data.length) * 100;

  // Prepare data for charts
  const glucoseData = {
    labels: data.map((_, index) => `Record ${index + 1}`),
    datasets: [
      {
        label: "Glucose Levels",
        data: data.map((record) => record.glucose),
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  const bmiData = {
    labels: ["Underweight", "Normal", "Overweight", "Obese"],
    datasets: [
      {
        label: "BMI Distribution",
        data: [
          data.filter((r) => r.bmi < 18.5).length,
          data.filter((r) => r.bmi >= 18.5 && r.bmi < 25).length,
          data.filter((r) => r.bmi >= 25 && r.bmi < 30).length,
          data.filter((r) => r.bmi >= 30).length,
        ],
        backgroundColor: [
          "rgba(255, 99, 132, 0.5)",
          "rgba(54, 162, 235, 0.5)",
          "rgba(255, 206, 86, 0.5)",
          "rgba(75, 192, 192, 0.5)",
        ],
      },
    ],
  };

  const ageData = {
    labels: ["0-20", "21-40", "41-60", "61-80", "81+"],
    datasets: [
      {
        label: "Age Distribution",
        data: [
          data.filter((r) => r.age <= 20).length,
          data.filter((r) => r.age > 20 && r.age <= 40).length,
          data.filter((r) => r.age > 40 && r.age <= 60).length,
          data.filter((r) => r.age > 60 && r.age <= 80).length,
          data.filter((r) => r.age > 80).length,
        ],
        backgroundColor: [
          "rgba(255, 99, 132, 0.5)",
          "rgba(54, 162, 235, 0.5)",
          "rgba(255, 206, 86, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(153, 102, 255, 0.5)",
        ],
      },
    ],
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Glucose Levels Over Time
            </Typography>
            <Line data={glucoseData} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              BMI Distribution
            </Typography>
            <Bar data={bmiData} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Age Distribution
            </Typography>
            <Pie data={ageData} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Risk Assessment</Typography>
              </Box>
              <Typography variant="body1" paragraph sx={{ pl: 4 }}>
                {analysis?.risk_assessment || "No risk assessment available."}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <InfoIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Recommendations</Typography>
              </Box>
              <List>
                {analysis?.recommendations &&
                analysis.recommendations.length > 0 ? (
                  analysis.recommendations.map((rec, index) => (
                    <ListItem key={index} sx={{ pl: 4 }}>
                      <ListItemIcon>
                        <CheckCircleIcon color="success" />
                      </ListItemIcon>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))
                ) : (
                  <ListItem sx={{ pl: 4 }}>
                    <ListItemText primary="No recommendations available." />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Preventive Measures</Typography>
              </Box>
              <List>
                {analysis?.preventive_measures &&
                analysis.preventive_measures.length > 0 ? (
                  analysis.preventive_measures.map((measure, index) => (
                    <ListItem key={index} sx={{ pl: 4 }}>
                      <ListItemIcon>
                        <CheckCircleIcon color="success" />
                      </ListItemIcon>
                      <ListItemText primary={measure} />
                    </ListItem>
                  ))
                ) : (
                  <ListItem sx={{ pl: 4 }}>
                    <ListItemText primary="No preventive measures available." />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Patient Records
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Age</TableCell>
                    <TableCell>BMI</TableCell>
                    <TableCell>Glucose</TableCell>
                    <TableCell>Diabetes</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.map((record) => (
                    <TableRow key={record.id}>
                      <TableCell>{record.id}</TableCell>
                      <TableCell>{record.age}</TableCell>
                      <TableCell>{record.bmi.toFixed(1)}</TableCell>
                      <TableCell>{record.glucose}</TableCell>
                      <TableCell>
                        {record.diabetes ? (
                          <Typography color="error">Yes</Typography>
                        ) : (
                          <Typography color="success">No</Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardCharts;
