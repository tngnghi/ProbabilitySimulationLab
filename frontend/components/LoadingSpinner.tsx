export default function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="spinner-container">
      <div className="spinner" />
      <p>{text}</p>
    </div>
  );
}
