import { Layout } from './components/Layout';
import { ParameterForm } from './components/ParameterForm';
import { ResultsDisplay } from './components/ResultsDisplay';
import { StepByStepView } from './components/StepByStepView';
import { ErrorAlert } from './components/ErrorAlert';
import { useBLS } from './hooks/useBLS';

function App() {
  const { result, error, loading, execute, clear } = useBLS();

  return (
    <Layout>
      <ParameterForm onSubmit={execute} loading={loading} />
      {error && <ErrorAlert message={error} onDismiss={clear} />}
      {result && (
        <>
          <ResultsDisplay result={result} />
          <StepByStepView result={result} />
        </>
      )}
    </Layout>
  );
}

export default App;
