export interface ActorIdentity {
  subject: string;
  kind: 'user' | 'service' | 'agent';
}
