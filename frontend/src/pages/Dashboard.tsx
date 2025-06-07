import { useState } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Box,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from "@mui/material";
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import { useQuery } from "@tanstack/react-query";
import { getAnalysisData, getDiabetesRecords } from "../services/api";
import type { DiabetesRecord } from "../types/analysis";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const Dashboard = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const {
    data: analysis,
    isLoading: isLoadingAnalysis,
    error: analysisError,
  } = useQuery({
    queryKey: ["analysisData"],
    queryFn: getAnalysisData,
  });

  const {
    data: records,
    isLoading: isLoadingRecords,
    error: recordsError,
  } = useQuery({
    queryKey: ["diabetesRecords"],
    queryFn: () => getDiabetesRecords(),
  });

  if (isLoadingAnalysis || isLoadingRecords) {
    return <CircularProgress />;
  }

  if (analysisError || recordsError) {
    return <Alert severity="error">Error loading data</Alert>;
  }

  // Ensure records is an array before filtering
  const recordsArray = Array.isArray(records) ? records : [];

  const filteredData = recordsArray.filter((item) =>
    Object.values(item).some((value) =>
      String(value).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Diabetes Analysis Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Records
              </Typography>
              <Typography variant="h5">
                {analysis?.total_records || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Positive Cases
              </Typography>
              <Typography variant="h5">
                {analysis?.positive_cases || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {analysis?.positive_rate?.toFixed(1) || "0.0"}% rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average BMI
              </Typography>
              <Typography variant="h5">
                {analysis?.average_bmi?.toFixed(1) || "0.0"}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Risk Assessment</Typography>
              </Box>
              <Typography variant="body1" paragraph sx={{ pl: 4 }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {analysis?.risk_assessment || "No risk assessment available."}
                </ReactMarkdown>
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
      </Grid>

      <TextField
        fullWidth
        label="Search"
        variant="outlined"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 3 }}
      />

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>BMI</TableCell>
              <TableCell>Glucose</TableCell>
              <TableCell>Outcome</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((row: DiabetesRecord) => (
              <TableRow key={row.id}>
                <TableCell>{row.id}</TableCell>
                <TableCell>{row.age}</TableCell>
                <TableCell>{row.bmi?.toFixed(1) || "0.0"}</TableCell>
                <TableCell>{row.glucose?.toFixed(1) || "0.0"}</TableCell>
                <TableCell>{row.outcome ? "Yes" : "No"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Dashboard;
