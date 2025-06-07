import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { format } from "date-fns";

export const exportDashboardToPDF = async (
  elementId: string,
  title: string = "Dashboard Report"
) => {
  const element = document.getElementById(elementId);
  if (!element) {
    throw new Error("Dashboard element not found");
  }

  try {
    // Create canvas from the dashboard element
    const canvas = await html2canvas(element, {
      scale: 2, // Higher scale for better quality
      useCORS: true, // Enable CORS for images
      logging: false,
    });

    // Calculate dimensions
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;

    // Create PDF
    const pdf = new jsPDF("p", "mm", "a4");
    const today = format(new Date(), "yyyy-MM-dd");

    // Add title and date
    pdf.setFontSize(20);
    pdf.text(title, 20, 20);
    pdf.setFontSize(12);
    pdf.text(`Generated on: ${today}`, 20, 30);

    // Add content
    pdf.addImage(
      canvas.toDataURL("image/jpeg", 1.0),
      "JPEG",
      0,
      40,
      imgWidth,
      imgHeight
    );

    // Add new pages if content is longer than one page
    while (heightLeft >= pageHeight) {
      position = heightLeft - pageHeight;
      pdf.addPage();
      pdf.addImage(
        canvas.toDataURL("image/jpeg", 1.0),
        "JPEG",
        0,
        -position,
        imgWidth,
        imgHeight
      );
      heightLeft -= pageHeight;
    }

    // Save the PDF
    pdf.save(`dashboard-report-${today}.pdf`);
  } catch (error) {
    console.error("Error generating PDF:", error);
    throw new Error("Failed to generate PDF report");
  }
};
