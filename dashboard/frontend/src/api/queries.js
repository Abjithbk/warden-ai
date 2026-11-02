import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as client from './client'

const LIVE_STATUSES = ['awaiting_approval', 'remediating']

export const useOverviewStats = () =>
    useQuery({
        queryKey: ['overview', 'stats'],
        queryFn: ({ signal }) => client.getOverviewStats(signal),
        refetchInterval: 15_000,
    })

export const useRecentActions = (limit = 5) =>
    useQuery({
        queryKey: ['overview', 'recent-actions', limit],
        queryFn: ({ signal }) => client.getRecentActions(limit, signal),
        refetchInterval: 15_000,
    })

export const useIncidents = (params) =>
    useQuery({
        queryKey: ['incidents', params],
        queryFn: ({ signal }) => client.getIncidents(params, signal),
        placeholderData: keepPreviousData,
    })

export const useIncident = (id) =>
    useQuery({
        queryKey: ['incident', id],
        queryFn: ({ signal }) => client.getIncidentById(id, signal),
        // poll only while a human (Slack click) or the executor can still change it
        refetchInterval: (query) => (LIVE_STATUSES.includes(query.state.data?.status) ? 5000 : false),
    })

export const useAuditLogs = (params) =>
    useQuery({
        queryKey: ['audit', params],
        queryFn: ({ signal }) => client.getAuditLogs(params, signal),
        placeholderData: keepPreviousData,
    })

export function useIncidentActions(id) {
    const qc = useQueryClient()
    // On success or failure (e.g. 409 "already decided in Slack") show the real state.
    const refresh = () => {
        qc.invalidateQueries({ queryKey: ['incident', id] })
        qc.invalidateQueries({ queryKey: ['incidents'] })
        qc.invalidateQueries({ queryKey: ['overview'] })
        qc.invalidateQueries({ queryKey: ['audit'] })
    }
    const actor = 'dashboard:operator' // TODO(auth): derive from the signed-in user

    return {
        approve: useMutation({
            mutationFn: () => client.approveIncident(id, { actioned_by: actor }),
            onSettled: refresh,
        }),
        reject: useMutation({
            mutationFn: (reason) => client.rejectIncident(id, { actioned_by: actor, reason }),
            onSettled: refresh,
        }),
        notify: useMutation({
            mutationFn: (force) => client.notifySlack(id, force),
            onSettled: refresh,
        }),
    }
}