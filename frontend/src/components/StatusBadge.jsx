export default function StatusBadge({ statusCode }) {
  if (statusCode === null || statusCode === undefined) {
    return (
      <span className="badge pending">
        <span className="dot" />
        Pending
      </span>
    );
  }

  if (statusCode < 400) {
    return (
      <span className="badge up">
        <span className="dot" />
        Up ({statusCode})
      </span>
    );
  }

  return (
    <span className="badge down">
      <span className="dot" />
      Down ({statusCode})
    </span>
  );
}
