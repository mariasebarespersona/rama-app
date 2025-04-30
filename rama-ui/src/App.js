import "bootstrap/dist/css/bootstrap.min.css";
import { useState } from "react";
import UploadForm from "./components/UploadForm";
import PropertySearch from "./components/PropertySearch";
import UploadPropertyDetails from "./components/UploadPropertyDetails";
import ChatBox from "./components/ChatBox";

function App() {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (newMessage) => {
    // Add user's message to state
    const updatedMessages = [...messages, { role: "user", content: newMessage }];
    setMessages(updatedMessages);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMessage }),
      });

      const data = await res.json();

      const finalMessages = [
        ...updatedMessages,
        { role: "assistant", content: data.reply || "Sorry, no response." },
      ];

      setMessages(finalMessages);
    } catch (error) {
      setMessages([
        ...updatedMessages,
        { role: "assistant", content: "Error: something went wrong." },
      ]);
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="text-center text-primary mb-4">🏡 RAMA Real Estate Management</h2>

      <div className="row">
        <div className="col-md-6">
          <UploadPropertyDetails />
        </div>

        <div className="col-md-6">
          <UploadForm />
        </div>

        <div className="col-md-6">
          <PropertySearch />
        </div>

        <div className="col-md-6">
          <ChatBox messages={messages} onSendMessage={handleSendMessage} />
        </div>
      </div>
    </div>
  );
}

export default App;



