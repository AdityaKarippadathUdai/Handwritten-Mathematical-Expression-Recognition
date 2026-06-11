import React from 'react';

interface ExpressionResultProps {
  latex: string;
}

export default function ExpressionResult({ latex }: ExpressionResultProps) {
  return (
    <div className="result-container" style={{ marginTop: '20px' }}>
      <h3>Recognized LaTeX Expression:</h3>
      <code>{latex}</code>
    </div>
  );
}
