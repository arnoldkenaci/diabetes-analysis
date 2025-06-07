import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { getInsights } from "../services/api";
import type { InsightsResult } from "../types/analysis";

const Analysis = () => {
  const {
    data: insights,
    isLoading,
    error,
  } = useQuery<InsightsResult>({
    queryKey: ["insights"],
    queryFn: getInsights,
  });

  if (isLoading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">Error loading insights</Alert>;
  }

  // Ensure insights and its properties exist
  const ageGroups = insights?.age_groups || [];
  const bmiCategories = insights?.bmi_categories || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Diabetes Analysis Insights
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Age Group Analysis
              </Typography>
              {ageGroups.map((group) => (
                <Box key={group.age_range} sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">
                    {group.age_range} years
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Count: {group.count}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Diabetes Rate: {group.diabetes_rate}%
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                BMI Category Analysis
              </Typography>
              {bmiCategories.map((category) => (
                <Box key={category.category} sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">
                    {category.category}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Count: {category.count}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Diabetes Rate: {category.diabetes_rate}%
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analysis;
