import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import HomeSearchBar from '../components/HomeSearchBar';
import jsPDF from 'jspdf';
import { ROUTES } from '../constants/routes';
import heroRobot from '../assets/hero-robot.jpg';

const Home = () => {
  const navigate = useNavigate();
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastQuery, setLastQuery] = useState('');

  const handleSearch = async (query: string, files: File[]) => {
    setIsLoading(true);
    setLastQuery(query);
    try {
      const formData = new FormData();
      formData.append('query', query);
      if (files && files.length > 0) {
        formData.append('file', files[0]);
      }

      const response = await fetch('/api/agents/chat', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      setSearchResults(result);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults({
        status: 'error',
        response: 'Failed to process your request. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const startSDLCWorkflow = () => {
    // Navigate to dashboard with the query as state
    navigate(ROUTES.DASHBOARD, { state: { prdText: lastQuery } });
  };

  const downloadPDF = () => {
    if (searchResults && searchResults.response) {
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      const maxLineWidth = pageWidth - (margin * 2);

      // Header
      doc.setFont("helvetica", "bold");
      doc.setFontSize(24);
      doc.setTextColor(37, 99, 235); // Accent blue
      doc.text("Coastal Seven AI Analysis", margin, 20);

      // Metadata
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text(`Generated on: ${new Date().toLocaleString()}`, margin, 32);

      // Decorative line
      doc.setDrawColor(230, 230, 230);
      doc.line(margin, 38, pageWidth - margin, 38);

      // Content
      doc.setFont("helvetica", "normal");
      doc.setFontSize(11);
      doc.setTextColor(33, 33, 33);

      const lines = doc.splitTextToSize(searchResults.response, maxLineWidth);
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

      // Footer on all pages (Optional, but professional)
      const pageCount = (doc as any).internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: "center" });
        doc.text("Coastal Seven Autonomous SDLC Platform", margin, pageHeight - 10);
      }

      doc.save('coastal_seven_analysis.pdf');
    }
  };

  return (
    <div className="min-h-screen pt-20 pb-12 bg-black text-white relative overflow-hidden">
      {/* Animated Background Gradients */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden bg-[rgb(17,27,51)]">
        <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-[rgb(17,85,120,0.2)] rounded-full blur-[120px] animate-pulse"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-[rgb(3,40,78,0.3)] rounded-full blur-[120px] animate-pulse [animation-delay:2s]"></div>
        <div className="absolute top-[20%] right-[20%] w-[40%] h-[40%] bg-[rgb(17,85,120,0.1)] rounded-full blur-[100px] animate-float"></div>
      </div>

      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:32px_32px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 pt-20">
        <div className="text-center space-y-8 mb-24">
          <div className="inline-block animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="relative group mx-auto mb-12">
              <div className="absolute -inset-4 bg-accent/20 rounded-full blur-[60px] opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
              <img
                src={heroRobot}
                alt="Hero AI"
                className="relative w-48 h-48 md:w-64 md:h-64 object-cover rounded-[3rem] mx-auto shadow-[0_0_50px_rgba(var(--color-accent-rgb),0.3)] border border-white/10 animate-float"
              />
            </div>
            <div className="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6">
              <span className="text-[10px] font-bold text-accent uppercase tracking-[0.3em]">Next-Gen SDLC Orchestration</span>
            </div>
          </div>

          <h1 className="text-6xl md:text-7xl font-black mb-8 leading-tight tracking-tighter animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
            What will <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-accent via-purple-400 to-indigo-500">
              Coastal Seven Build?
            </span>
          </h1>

          <p className="text-zinc-500 text-lg md:text-xl max-w-2xl mx-auto font-medium leading-relaxed animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
            Describe your software vision, and our 7-agent autonomous SDLC pipeline will handle everything from architecture to code review.
          </p>
        </div>


        <div className="mb-32 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-900">

          <div className="max-w-4xl mx-auto">
            <HomeSearchBar onSearch={handleSearch} isLoading={isLoading} />

            {/* Search Results (GPT Style) */}
            {searchResults && (
              <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="flex gap-6 max-w-4xl">
                  <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center shrink-0 shadow-[0_10px_30px_rgba(37,99,235,0.3)]">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="flex-1 space-y-3 pt-1">
                    <div className="flex items-center justify-between">
                      <div className="text-zinc-500 text-[10px] font-black uppercase tracking-[0.3em]">
                        Coastal Seven Intelligence
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={downloadPDF}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-bold text-zinc-400 hover:text-white hover:bg-white/10 transition-all active:scale-95"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download PDF
                        </button>
                        <button
                          onClick={startSDLCWorkflow}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent/20 border border-accent/30 text-xs font-bold text-accent hover:bg-accent hover:text-white transition-all active:scale-95 shadow-[0_0_20px_rgba(37,99,235,0.2)]"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          Start Full SDLC
                        </button>
                      </div>
                    </div>
                    <div className="text-zinc-200 text-lg leading-relaxed whitespace-pre-wrap">
                      {searchResults.response}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Features Split */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 pt-12 border-t border-white/5 pb-24">
          {[
            { title: "7 Specialized Agents", desc: "UI/UX, Architecture, Impact Analysis, Coding, Testing, Security Scanning, and Code Review agents working in perfect harmony." },
            { title: "Full Automation", desc: "Upload PRD → Get complete project with code, tests, documentation, and GitHub repository. Zero manual intervention required." },
            { title: "Production Ready", desc: "Generated code follows best practices with comprehensive testing, security scanning, and professional documentation." }
          ].map((f, i) => (
            <div key={i} className="space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-3">
                <span className="w-1.5 h-1.5 bg-accent rounded-full" />
                {f.title}
              </h3>
              <p className="text-zinc-500 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
