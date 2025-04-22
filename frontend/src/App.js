import { useState } from "react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Template data
const TEMPLATES = [
  {
    id: "landing-page",
    name: "Landing Page",
    description: "A sleek single-page website perfect for showcasing your product or service",
    preview_url: "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80",
    type: "landing"
  },
  {
    id: "multi-page",
    name: "Multi-Page Website",
    description: "A complete website with navigation menu and multiple pages",
    preview_url: "https://images.unsplash.com/photo-1522542550221-31fd19575a2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80",
    type: "multi-page"
  },
  {
    id: "portfolio",
    name: "Portfolio",
    description: "Showcase your work with this elegant portfolio template",
    preview_url: "https://images.unsplash.com/photo-1558655146-d09347e92766?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80",
    type: "portfolio"
  },
  {
    id: "blog",
    name: "Blog",
    description: "Share your thoughts with a clean, reader-friendly blog design",
    preview_url: "https://images.unsplash.com/photo-1499750310107-5fef28a66643?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80",
    type: "blog"
  },
  {
    id: "dashboard",
    name: "Dashboard",
    description: "Data-focused layout ideal for analytics and reporting",
    preview_url: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80",
    type: "dashboard"
  }
];

function App() {
  const [step, setStep] = useState("start"); // start, template, details, preview
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [notionPageId, setNotionPageId] = useState("");
  const [notionToken, setNotionToken] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [websiteData, setWebsiteData] = useState(null);
  const [aiPrompt, setAiPrompt] = useState("");

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setStep("details");
  };

  const handleBackToTemplates = () => {
    setStep("template");
  };

  const handleBackToStart = () => {
    setStep("start");
  };

  const handleGenerateWebsite = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Call the backend API to convert Notion page to website
      const response = await fetch(`${BACKEND_URL}/api/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page_id: notionPageId,
          template_id: selectedTemplate.id,
          notion_token: notionToken || undefined
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate website');
      }

      const data = await response.json();
      setWebsiteData(data);
      setIsLoading(false);
      setStep("preview");
    } catch (err) {
      setError(err.message || 'An error occurred');
      setIsLoading(false);
    }
  };

  const handleAICustomization = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/customize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          website_id: websiteData.website_id,
          prompt: aiPrompt
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to customize website');
      }

      const data = await response.json();
      
      // Show a success message or update the preview
      alert(`Changes applied: ${data.message}`);
      
      // Clear the prompt field
      setAiPrompt("");
      setIsLoading(false);
    } catch (err) {
      setError(err.message || 'An error occurred');
      setIsLoading(false);
    }
  };

  return (
    <div className="App min-h-screen bg-gray-900 text-gray-200">
      <header className="App-header py-6 border-b border-gray-800">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">
            <span className="text-yellow-400">Notion</span> to <span className="text-lime-400">Website</span>
          </h1>
          <p className="mt-2">Transform your Notion pages into beautiful websites in seconds</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {step === "start" && (
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Turn Your Notion Pages Into Stunning Websites</h2>
            <p className="text-xl mb-8">
              No coding required. Just select a template, enter your Notion page URL, and we'll do the rest.
            </p>
            
            <div className="mb-10">
              <h3 className="text-2xl font-semibold mb-4">How It Works</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 p-6 rounded-lg">
                  <div className="text-yellow-400 text-4xl font-bold mb-3">1</div>
                  <h4 className="text-xl font-semibold mb-2">Select a Template</h4>
                  <p>Choose from our collection of professionally designed website templates</p>
                </div>
                <div className="bg-gray-800 p-6 rounded-lg">
                  <div className="text-yellow-400 text-4xl font-bold mb-3">2</div>
                  <h4 className="text-xl font-semibold mb-2">Connect Notion</h4>
                  <p>Enter your Notion page URL and authenticate if needed</p>
                </div>
                <div className="bg-gray-800 p-6 rounded-lg">
                  <div className="text-yellow-400 text-4xl font-bold mb-3">3</div>
                  <h4 className="text-xl font-semibold mb-2">Generate & Customize</h4>
                  <p>Preview your website and customize with our AI assistant</p>
                </div>
              </div>
            </div>
            
            <button 
              className="bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold py-3 px-8 rounded-lg text-xl transition-colors"
              onClick={() => setStep("template")}
            >
              Get Started
            </button>
          </div>
        )}

        {step === "template" && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-3xl font-bold">Select a Template</h2>
              <button 
                className="text-yellow-400 hover:text-yellow-300"
                onClick={handleBackToStart}
              >
                Back to Start
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {TEMPLATES.map((template) => (
                <div 
                  key={template.id}
                  className="bg-gray-800 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-yellow-400 transition-all"
                  onClick={() => handleTemplateSelect(template)}
                >
                  <div className="h-48 bg-gray-700 overflow-hidden">
                    <img 
                      src={template.preview_url} 
                      alt={`${template.name} template`}
                      className="w-full h-full object-cover hover:scale-105 transition-transform"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.parentElement.innerHTML = `<div class="flex items-center justify-center h-full"><span class="text-2xl text-gray-500">${template.name}</span></div>`;
                      }}
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="text-xl font-semibold mb-2">{template.name}</h3>
                    <p className="text-gray-400">{template.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === "details" && selectedTemplate && (
          <div className="max-w-2xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-3xl font-bold">Enter Notion Details</h2>
              <button 
                className="text-yellow-400 hover:text-yellow-300"
                onClick={handleBackToTemplates}
              >
                Back to Templates
              </button>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg mb-6">
              <h3 className="text-xl font-semibold mb-4">Selected Template: {selectedTemplate.name}</h3>
              <p className="text-gray-400 mb-2">{selectedTemplate.description}</p>
            </div>
            
            <form onSubmit={handleGenerateWebsite} className="bg-gray-800 p-6 rounded-lg">
              <div className="mb-6">
                <label htmlFor="notionPageId" className="block text-xl mb-2">Notion Page URL or ID</label>
                <input
                  type="text"
                  id="notionPageId"
                  className="w-full bg-gray-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-yellow-400 focus:outline-none"
                  placeholder="https://www.notion.so/mypage or page_id"
                  value={notionPageId}
                  onChange={(e) => setNotionPageId(e.target.value)}
                  required
                />
                <p className="text-gray-400 mt-2 text-sm">
                  Enter the full URL of your Notion page or just the page ID
                </p>
              </div>
              
              <div className="mb-6">
                <label htmlFor="notionToken" className="block text-xl mb-2">Notion API Token (for private pages)</label>
                <input
                  type="password"
                  id="notionToken"
                  className="w-full bg-gray-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-yellow-400 focus:outline-none"
                  placeholder="Optional: For private pages"
                  value={notionToken}
                  onChange={(e) => setNotionToken(e.target.value)}
                />
                <p className="text-gray-400 mt-2 text-sm">
                  If your page is private, you'll need to provide an API token
                </p>
              </div>
              
              {error && (
                <div className="mb-6 bg-red-900/50 text-red-200 p-4 rounded-lg">
                  {error}
                </div>
              )}
              
              <button
                type="submit"
                className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold py-3 px-8 rounded-lg text-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isLoading || !notionPageId}
              >
                {isLoading ? "Generating..." : "Generate Website"}
              </button>
            </form>
          </div>
        )}

        {step === "preview" && websiteData && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-3xl font-bold">Your Website Preview</h2>
              <button 
                className="text-yellow-400 hover:text-yellow-300"
                onClick={handleBackToTemplates}
              >
                Create Another
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="bg-gray-800 rounded-lg overflow-hidden">
                  <div className="p-8 bg-gray-700">
                    {websiteData.content ? (
                      <div className="bg-white text-gray-900 rounded-lg p-6 mx-auto max-w-4xl min-h-[400px] shadow-lg">
                        <h1 className="text-3xl font-bold mb-6">{websiteData.content.title || "My Website"}</h1>
                        
                        {websiteData.content.blocks && websiteData.content.blocks.map((block, index) => {
                          switch(block.type) {
                            case "heading":
                              return <h2 key={index} className="text-2xl font-semibold my-4">{block.content}</h2>
                            case "paragraph":
                              return <p key={index} className="my-3">{block.content}</p>
                            case "image":
                              return (
                                <div key={index} className="my-6">
                                  <img 
                                    src={block.url} 
                                    alt="Content" 
                                    className="rounded-lg max-w-full mx-auto"
                                    onError={(e) => {
                                      e.target.onerror = null;
                                      e.target.src = "https://images.unsplash.com/photo-1499750310107-5fef28a66643";
                                    }}
                                  />
                                </div>
                              )
                            default:
                              return <p key={index}>{block.content}</p>
                          }
                        })}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-96">
                        <span className="text-2xl text-gray-500">Loading website preview...</span>
                      </div>
                    )}
                  </div>
                  <div className="p-5">
                    <h3 className="text-2xl font-semibold mb-2">Your Generated Website</h3>
                    <p className="text-gray-400 mb-4">
                      Website ID: {websiteData.website_id}
                    </p>
                    <div className="flex space-x-4">
                      <button className="bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold py-2 px-4 rounded transition-colors">
                        Edit Design
                      </button>
                      <button className="bg-lime-400 hover:bg-lime-500 text-gray-900 font-bold py-2 px-4 rounded transition-colors">
                        Publish Website
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <div className="bg-gray-800 p-6 rounded-lg mb-6">
                  <h3 className="text-xl font-semibold mb-4">AI Customization Assistant</h3>
                  <p className="text-gray-400 mb-4">
                    Tell our AI what changes you'd like to make
                  </p>
                  
                  <form onSubmit={handleAICustomization}>
                    <textarea
                      className="w-full bg-gray-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-yellow-400 focus:outline-none min-h-[120px]"
                      placeholder="e.g., 'Make the header larger' or 'Change the background color to blue'"
                      value={aiPrompt}
                      onChange={(e) => setAiPrompt(e.target.value)}
                      required
                    />
                    
                    <button
                      type="submit"
                      className="mt-4 w-full bg-lime-400 hover:bg-lime-500 text-gray-900 font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={isLoading || !aiPrompt}
                    >
                      {isLoading ? "Applying..." : "Apply Changes"}
                    </button>
                  </form>
                </div>
                
                <div className="bg-gray-800 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold mb-4">Next Steps</h3>
                  <ul className="space-y-3 text-gray-400">
                    <li className="flex items-start">
                      <span className="text-yellow-400 mr-2">•</span>
                      Customize your website using the AI assistant
                    </li>
                    <li className="flex items-start">
                      <span className="text-yellow-400 mr-2">•</span>
                      Preview your changes in real-time
                    </li>
                    <li className="flex items-start">
                      <span className="text-yellow-400 mr-2">•</span>
                      Publish when you're ready to go live
                    </li>
                    <li className="flex items-start">
                      <span className="text-yellow-400 mr-2">•</span>
                      Share your new website with the world
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-gray-800 py-6 mt-16">
        <div className="container mx-auto px-4 text-center text-gray-400">
          <p>© 2025 Notion to Website Converter. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
