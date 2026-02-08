interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
}

export function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="px-4 py-3 mb-4 bg-red-50 border border-red-200 rounded-lg text-red-800 flex justify-between items-start gap-3">
      <div>
        <strong>Error: </strong>
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="bg-transparent border-none cursor-pointer text-red-800 text-lg leading-none"
        >
          &times;
        </button>
      )}
    </div>
  );
}
