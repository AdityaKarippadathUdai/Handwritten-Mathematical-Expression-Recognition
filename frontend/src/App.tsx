import React, { useState } from 'react';
import Canvas from './components/canvas/Canvas.tsx';
import ExpressionResult from './components/expression/ExpressionResult.tsx';

function App() {
  const [latex, setLatex] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleRecognize = async (imageBlob: Blob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', imageBlob, 'canvas.png');
      
      const response = await fetch('/api/v1/expressions/recognize', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setLatex(data.latex || '');
    } catch (error) {
      console.error("Recognition failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Handwritten Mathematical Expression Recognizer</h1>
      </header>
      <main>
        <Canvas onRecognize={handleRecognize} loading={loading} />
        {latex && <ExpressionResult latex={latex} />}
      </main>
    </div>
  );
}

export default App;
