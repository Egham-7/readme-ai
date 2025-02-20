import { useUser } from "@/hooks/users/use-user";
import { Coins } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { UserButton } from "@clerk/clerk-react";

interface UserProfileProps {}

export function UserProfile({}: UserProfileProps) {
  const { data: user, isLoading } = useUser();

  if (isLoading) {
    return <UserProfileSkeleton />;
  }

  return (
    <div className="w-full p-2">
      <div className="rounded-lg bg-gradient-to-br from-primary/10 via-primary/5 to-background border border-border p-3">
        <div className="flex items-center gap-3">
          <UserButton />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {user?.clerkUser.fullName || user?.clerkUser.username}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {user?.clerkUser.emailAddresses.at(-1)?.emailAddress}
            </p>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2">
          <Coins className="h-4 w-4 text-primary" />
          <span className="text-sm text-muted-foreground">
            {user?.tokens_balance ?? 0} Credits
          </span>
        </div>
      </div>
    </div>
  );
}

function UserProfileSkeleton() {
  return (
    <div className="w-full p-2">
      <div className="rounded-lg bg-gradient-to-br from-primary/10 via-primary/5 to-background border border-border p-3">
        <div className="flex items-center gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
        <div className="mt-3">
          <Skeleton className="h-4 w-20" />
        </div>
      </div>
    </div>
  );
}
