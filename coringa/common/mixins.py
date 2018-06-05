#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rest_framework import viewsets, mixins, permissions
from django.shortcuts import get_object_or_404
from django import http


class ShowOnlyUserObjectsMixin(object):
    def get_queryset(self):
        user = self.request.user
        queryset = super(ShowOnlyUserObjectsMixin, self).get_queryset()
        return queryset.filter(user=user)


class CreateModelWithUserMixin(mixins.CreateModelMixin):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreateFormWithUserMixin(object):
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return http.HttpResponseRedirect(self.get_success_url())


class NestedLedgerMixin(ShowOnlyUserObjectsMixin,
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    ledger_id = None

    def get_ledger(self, request, ledger_pk):
        from ledgers.models import Ledger
        ledger = get_object_or_404(Ledger.objects.filter(user=request.user), pk=ledger_pk)
        self.ledger_id = ledger.id
        return ledger

    def create(self, request, *args, **kwargs):
        self.get_ledger(request, ledger_pk=kwargs['ledger_pk'])
        return super(NestedLedgerMixin, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(ledger_id=self.ledger_id, user=self.request.user)

    def get_queryset(self):
        queryset = super(NestedLedgerMixin, self).get_queryset()
        return queryset.filter(ledger_id=self.ledger_id)

    def list(self, request, *args, **kwargs):
        self.get_ledger(request, ledger_pk=kwargs['ledger_pk'])
        return super(NestedLedgerMixin, self).list(request, *args, **kwargs)
