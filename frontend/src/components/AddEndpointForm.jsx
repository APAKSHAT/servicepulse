import { useState } from "react";

export default function AddEndpointForm({ onSubmit, onCancel }) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [interval, setInterval] = useState(30);

  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim() || !url.trim()) return;
    onSubmit({ name: name.trim(), url: url.trim(), interval_seconds: interval });
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Add Endpoint</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="ep-name">Name</label>
              <input
                id="ep-name"
                type="text"
                placeholder="My API"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="ep-url">URL</label>
              <input
                id="ep-url"
                type="url"
                placeholder="https://api.example.com/health"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="ep-interval">Check interval (seconds)</label>
              <input
                id="ep-interval"
                type="number"
                min={5}
                max={3600}
                value={interval}
                onChange={(e) => setInterval(Number(e.target.value))}
              />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Add Endpoint
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
