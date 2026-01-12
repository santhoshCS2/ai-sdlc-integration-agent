
import jsPDF from 'jspdf';

export const generatePDF = (title: string, content: string) => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxLineWidth = pageWidth - (margin * 2);

    // Header
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(37, 99, 235);
    doc.text(title, margin, 20);

    // Branding
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(150, 150, 150);
    doc.text("coastalsevel Autonomous SDLC Platform Output", margin, 32);

    // Decorative line
    doc.setDrawColor(230, 230, 230);
    doc.line(margin, 38, pageWidth - margin, 38);

    // Content
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.setTextColor(33, 33, 33);

    const lines = doc.splitTextToSize(content, maxLineWidth);
    let cursorY = 50;
    const lineHeight = 7;

    lines.forEach((line: string) => {
        if (cursorY > pageHeight - margin) {
            doc.addPage();
            cursorY = margin;
        }
        doc.text(line, margin, cursorY);
        cursorY += lineHeight;
    });

    // Add page numbers
    const pageCount = (doc as any).internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        const footerText = `Page ${i} of ${pageCount}`;
        doc.text(footerText, pageWidth / 2, pageHeight - 10, { align: "center" });
    }

    doc.save(`${title.toLowerCase().replace(/\s+/g, '_')}_output.pdf`);
};
