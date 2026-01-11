import { LampContainer } from "../ui/lamp";
import { motion } from "motion/react";

function Hero() {
  return (
    <LampContainer>
      <motion.h1
        initial={{ opacity: 0.5, y: 100 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{
          delay: 0.3,
          duration: 0.8,
          ease: "easeInOut",
        }}
        className="mt-8 bg-gradient-to-br from-slate-300 to-slate-500 py-4 bg-clip-text text-center text-4xl font-medium tracking-tight text-transparent md:text-7xl"
      >
        <div className="py-4 px-6 flex flex-col gap-10 justify-center items-center">
          <h1 className="text-5xl font-semibold text-center max-w-3xl leading-tight text-foreground">
            Your Own Knowledge Base
          </h1>
          <h2 className="text-4xl font-medium text-center max-w-3xl leading-tight text-foreground">
            Convert documents into embeddings and unlock intelligent,
            context-aware responses from AI agents.
          </h2>
        </div>
      </motion.h1>
    </LampContainer>
  );
}
export default Hero;
