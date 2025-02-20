import type { UserResource } from "@clerk/types";
import { API_BASE_URL } from "./utils";
import { ApiError } from "./utils";

export interface User {
  id: number;
  clerk_id: string;
  email: string;
  tokens_balance: number;
  tokens_last_reset: string;
  stripe_customer_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CombinedUser extends Partial<User> {
  clerkUser: UserResource;
}

export interface UserUpdate {
  email?: string;
  tokens_balance?: number;
  stripe_customer_id?: string;
}

export const userService = {
  async getUserById(id: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${id}`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new ApiError(
        "Failed to fetch user",
        "USER_NOT_FOUND",
        { status_code: response.status, user_id: id },
        new Date().toISOString(),
      );
    }

    return response.json();
  },

  async updateUser(id: number, data: UserUpdate): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${id}`, {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new ApiError(
        "Failed to update user",
        "VALIDATION_ERROR",
        { status_code: response.status, user_id: id, update_data: data },
        new Date().toISOString(),
      );
    }

    return response.json();
  },

  async deleteUser(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/users/${id}`, {
      method: "DELETE",
      credentials: "include",
    });

    if (!response.ok) {
      throw new ApiError(
        "Failed to delete user",
        "FORBIDDEN",
        { status_code: response.status, user_id: id },
        new Date().toISOString(),
      );
    }
  },
};
