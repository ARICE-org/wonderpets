import React from 'react';
import { Toast, ToastTitle, ToastDescription, HStack, VStack, Spinner, useToast } from '@gluestack-ui/themed';
import { Ionicons } from '@expo/vector-icons';

/**
 * Global Toast Service
 * Allows triggering toasts from anywhere (components or services)
 */

type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastOptions {
    id?: string;
    title: string;
    description?: string;
    duration?: number | null;
    placement?: 'top' | 'bottom' | 'top left' | 'top right' | 'bottom left' | 'bottom right';
}

// Internal reference to the toast object from useToast()
let toastInstance: any = null;

export interface ToastService {
    setInstance: (instance: any) => void;
    showSuccess: (options: ToastOptions | string) => string | null;
    showError: (options: ToastOptions | string) => string | null;
    showInfo: (options: ToastOptions | string) => string | null;
    show: (options: ToastOptions & { type?: ToastType }) => string | null;
    showLoading: (title: string, description?: string) => string | null;
    close: (id: string) => void;
    closeAll: () => void;
}

export const toastService: ToastService = {
    /**
     * Internal method to set the toast instance from a hook
     */
    setInstance: (instance: any) => {
        toastInstance = instance;
    },

    /**
     * Show a success toast
     */
    showSuccess: (options: ToastOptions | string) => {
        const opts = typeof options === 'string' ? { title: options } : options;
        return toastService.show({ ...opts, type: 'success' });
    },

    /**
     * Show an error toast
     */
    showError: (options: ToastOptions | string) => {
        const opts = typeof options === 'string' ? { title: options } : options;
        return toastService.show({ ...opts, type: 'error' });
    },

    /**
     * Show an info toast
     */
    showInfo: (options: ToastOptions | string) => {
        const opts = typeof options === 'string' ? { title: options } : options;
        return toastService.show({ ...opts, type: 'info' });
    },

    /**
     * Core show method
     */
    show: (options: ToastOptions & { type?: ToastType }) => {
        if (!toastInstance) {
            console.warn('Toast instance not initialized. Call toastService.setInstance(useToast()) first.');
            return null;
        }

        const { title, description, type = 'info', placement = 'top', duration = 5000 } = options;

        const bgMap: Record<string, string> = {
            success: '$green600',
            error: '$red600',
            info: '$blue600',
            warning: '$orange600',
        };

        const iconMap: Record<string, any> = {
            success: 'checkmark-circle' as const,
            error: 'alert-circle' as const,
            info: 'information-circle' as const,
            warning: 'warning' as const,
        };

        return toastInstance.show({
            placement,
            duration,
            render: ({ id }: { id: string }) => {
                const toastId = 'toast-' + id;
                return (
                    <Toast nativeID={toastId} action={type === 'info' ? 'muted' : (type as any)} variant="solid" bg={bgMap[type]} p="$4" borderRadius="$lg">
                        <VStack space="xs">
                            <HStack space="xs" alignItems="center">
                                <Ionicons name={iconMap[type]} size={20} color="white" />
                                <ToastTitle color="$white" fontWeight="$bold">{title}</ToastTitle>
                            </HStack>
                            {description && (
                                <ToastDescription color="$white">
                                    {description}
                                </ToastDescription>
                            )}
                        </VStack>
                    </Toast>
                );
            },
        });
    },

    /**
     * Show a loading/uploading toast
     */
    showLoading: (title: string, description?: string) => {
        if (!toastInstance) return null;

        return toastInstance.show({
            placement: 'bottom',
            duration: null,
            render: ({ id }: { id: string }) => {
                return (
                    <Toast nativeID={id} action="info" variant="solid" bg="$blue600" p="$4" borderRadius="$lg" mb="$20">
                        <HStack space="md" alignItems="center">
                            <Spinner color="$white" size="small" />
                            <VStack>
                                <ToastTitle color="$white" fontWeight="$bold">{title}</ToastTitle>
                                {description && <ToastDescription color="$white">{description}</ToastDescription>}
                            </VStack>
                        </HStack>
                    </Toast>
                );
            },
        });
    },

    /**
     * Close a specific toast
     */
    close: (id: string) => {
        if (toastInstance && id) {
            toastInstance.close(id);
        }
    },

    /**
     * Close all toasts
     */
    closeAll: () => {
        if (toastInstance) {
            toastInstance.closeAll();
        }
    }
};
