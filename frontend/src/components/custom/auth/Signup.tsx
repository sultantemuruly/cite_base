import { useState } from "react";
import { useNavigate } from "react-router";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

const formSchema = z
  .object({
    email: z.string().email("Enter a valid email").max(100),
    password: z
      .string()
      .min(6, "Password must be at least 6 characters.")
      .max(72, "Password must be at most 72 characters."),
    confirmPassword: z
      .string()
      .min(6, "Password must be at least 6 characters.")
      .max(72, "Password must be at most 72 characters."),
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: "Passwords must match.",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof formSchema>;

function Signup() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (values: FormValues) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: values.email,
          password: values.password,
        }),
      });

      if (!response.ok) {
        setLoading(false);
        throw new Error("Failed to sign up");
      }

      const token_response = await fetch("http://localhost:8000/auth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: values.email,
          password: values.password,
        }),
      });

      if (!token_response.ok) {
        setLoading(false);
        throw new Error("Failed to sign in");
      }

      const data = await token_response.json();
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } catch (error) {
      setLoading(false);
      console.error("Signin error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="you@example.com"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="••••••••" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Repeat Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="••••••••" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button disabled={loading} className="w-full" type="submit">
            {loading ? "Signing up..." : "Create an account"}
          </Button>

          <p className="text-center">
            Already have an account?{" "}
            <a href="/auth/signin" className="text-blue-500">
              Sign in
            </a>
          </p>
        </form>
      </Form>
    </div>
  );
}

export default Signup;
