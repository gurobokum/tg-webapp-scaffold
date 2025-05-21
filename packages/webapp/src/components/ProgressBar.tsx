import { motion } from "framer-motion";

const ProgressBar = ({
  currentStep,
  totalSteps,
}: {
  currentStep: number;
  totalSteps: number;
}) => {
  const start = ((currentStep - 1) / (totalSteps + 1)) * 100;
  const end = (currentStep / (totalSteps + 1)) * 100;

  return (
    <div className="w-screen">
      <div className="h-2 bg-base-300">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: `${start}%` }}
          animate={{ width: `${end}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
