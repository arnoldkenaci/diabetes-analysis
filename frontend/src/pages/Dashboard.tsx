import { Box, Grid, Paper, Typography, Button } from "@mui/material";
import { FileUpload } from "../components/FileUpload";
import DashboardCharts from "../components/DashboardCharts";
import { useQuery } from "@tanstack/react-query";
import { getDiabetesRecords } from "../services/api";
import { exportDashboardToPDF } from "../services/pdfExport";
import { Download as DownloadIcon } from "@mui/icons-material";

const Dashboard = () => {
  const {
    data: records = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["diabetesRecords"],
    queryFn: () => getDiabetesRecords(),
  });

  const handleUploadSuccess = () => {
    refetch();
  };

  const handleExportPDF = async () => {
    try {
      await exportDashboardToPDF(
        "dashboard-content",
        "Diabetes Analysis Dashboard"
      );
    } catch (error) {
      console.error("Failed to export PDF:", error);
    }
  };

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h5">Dashboard</Typography>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={handleExportPDF}
              >
                Export to PDF
              </Button>
            </Box>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <div id="dashboard-content">
            <DashboardCharts records={records} />
          </div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
