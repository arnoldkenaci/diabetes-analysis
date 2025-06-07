import { ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  AppBar,
  Box,
  Container,
  Toolbar,
  Typography,
  Button,
  IconButton,
  useTheme,
} from "@mui/material";
import { Menu as MenuIcon } from "@mui/icons-material";

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        width: "100vw",
      }}
    >
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Diabetes Analysis Dashboard
          </Typography>
          <Button
            color="inherit"
            onClick={() => navigate("/")}
            sx={{
              backgroundColor: isActive("/")
                ? "rgba(255, 255, 255, 0.1)"
                : "transparent",
            }}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            onClick={() => navigate("/analysis")}
            sx={{
              backgroundColor: isActive("/analysis")
                ? "rgba(255, 255, 255, 0.1)"
                : "transparent",
            }}
          >
            Analysis
          </Button>
        </Toolbar>
      </AppBar>
      <Container
        component="main"
        maxWidth="xl"
        sx={{
          flexGrow: 1,
          py: 3,
          backgroundColor: theme.palette.background.default,
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default Layout;
